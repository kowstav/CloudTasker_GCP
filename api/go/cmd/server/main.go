package main

import (
    "context"
    "database/sql"
    "encoding/json"
    "fmt"
    "log"
    "net"
    "os"
    "time"

    "cloud.google.com/go/pubsub"
    pb "github.com/kowstav/cloudtasker/api/go/proto"
    _ "github.com/lib/pq"
    "google.golang.org/grpc"
)

type server struct {
    pb.UnimplementedTaskServiceServer
    db          *sql.DB
    pubsubTopic *pubsub.Topic
}

func (s *server) CreateTask(ctx context.Context, req *pb.CreateTaskRequest) (*pb.CreateTaskResponse, error) {
    // Begin transaction
    tx, err := s.db.BeginTx(ctx, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to begin transaction: %v", err)
    }
    defer tx.Rollback()

    // Insert task into database
    var jobID int64
    now := time.Now().UTC()
    err = tx.QueryRowContext(
        ctx,
        `INSERT INTO jobs (payload, status, created_at, updated_at)
         VALUES ($1, $2, $3, $3)
         RETURNING id`,
        req.Payload, "PENDING", now,
    ).Scan(&jobID)

    if err != nil {
        return nil, fmt.Errorf("failed to insert task: %v", err)
    }

    // Prepare message for Pub/Sub
    message := struct {
        JobID   int64  `json:"job_id"`
        Payload string `json:"payload"`
    }{
        JobID:   jobID,
        Payload: req.Payload,
    }

    messageBytes, err := json.Marshal(message)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal message: %v", err)
    }

    // Publish to Pub/Sub
    result := s.pubsubTopic.Publish(ctx, &pubsub.Message{
        Data: messageBytes,
    })

    _, err = result.Get(ctx)
    if err != nil {
        return nil, fmt.Errorf("failed to publish message: %v", err)
    }

    // Commit transaction
    if err = tx.Commit(); err != nil {
        return nil, fmt.Errorf("failed to commit transaction: %v", err)
    }

    return &pb.CreateTaskResponse{
        JobId:  jobID,
        Status: "PENDING",
    }, nil
}

func (s *server) GetTask(ctx context.Context, req *pb.GetTaskRequest) (*pb.GetTaskResponse, error) {
    var status, result string
    var createdAt, updatedAt time.Time

    err := s.db.QueryRowContext(
        ctx,
        `SELECT status, result, created_at, updated_at
         FROM jobs
         WHERE id = $1`,
        req.JobId,
    ).Scan(&status, &result, &createdAt, &updatedAt)

    if err == sql.ErrNoRows {
        return nil, fmt.Errorf("task not found")
    }
    if err != nil {
        return nil, fmt.Errorf("failed to query task: %v", err)
    }

    return &pb.GetTaskResponse{
        JobId:     req.JobId,
        Status:    status,
        Result:    result,
        CreatedAt: createdAt.Format(time.RFC3339),
        UpdatedAt: updatedAt.Format(time.RFC3339),
    }, nil
}

func main() {
    // Initialize database connection
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatalf("Failed to connect to database: %v", err)
    }
    defer db.Close()

    // Initialize Pub/Sub client
    ctx := context.Background()
    pubsubClient, err := pubsub.NewClient(ctx, os.Getenv("PROJECT_ID"))
    if err != nil {
        log.Fatalf("Failed to create pubsub client: %v", err)
    }
    defer pubsubClient.Close()

    topic := pubsubClient.Topic(os.Getenv("PUBSUB_TOPIC"))
    defer topic.Stop()

    // Initialize gRPC server
    lis, err := net.Listen("tcp", fmt.Sprintf(":%s", os.Getenv("PORT")))
    if err != nil {
        log.Fatalf("Failed to listen: %v", err)
    }

    s := grpc.NewServer()
    pb.RegisterTaskServiceServer(s, &server{
        db:          db,
        pubsubTopic: topic,
    })

    log.Printf("Server listening at %v", lis.Addr())
    if err := s.Serve(lis); err != nil {
        log.Fatalf("Failed to serve: %v", err)
    }
}