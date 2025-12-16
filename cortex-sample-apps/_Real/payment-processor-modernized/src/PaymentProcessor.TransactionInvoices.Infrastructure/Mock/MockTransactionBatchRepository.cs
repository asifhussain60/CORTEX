using System.Collections.Concurrent;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of ITransactionBatchRepository.
/// Thread-safe batch state management for testing.
/// </summary>
public class MockTransactionBatchRepository : ITransactionBatchRepository
{
    private readonly ConcurrentDictionary<string, TransactionBatch> _batches = new();

    public Task<TransactionBatch?> GetByIdAsync(string batchId)
    {
        _batches.TryGetValue(batchId, out var batch);
        return Task.FromResult(batch);
    }

    public Task<IEnumerable<TransactionBatch>> GetAllAsync()
    {
        return Task.FromResult(_batches.Values.AsEnumerable());
    }

    public Task<IEnumerable<TransactionBatch>> GetByStatusAsync(string status)
    {
        var batches = _batches.Values.Where(b => b.Status == status);
        return Task.FromResult(batches);
    }

    public Task<IEnumerable<TransactionBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        var batches = _batches.Values.Where(b => 
            b.CreatedDate >= startDate && b.CreatedDate <= endDate);
        return Task.FromResult(batches);
    }

    public Task<TransactionBatch> CreateAsync(TransactionBatch batch)
    {
        if (string.IsNullOrEmpty(batch.BatchId))
        {
            batch.BatchId = $"BATCH-{Guid.NewGuid():N}";
        }

        batch.CreatedDate = DateTime.UtcNow;

        if (!_batches.TryAdd(batch.BatchId, batch))
        {
            throw new InvalidOperationException($"Batch with ID {batch.BatchId} already exists");
        }

        return Task.FromResult(batch);
    }

    public Task<TransactionBatch> UpdateAsync(TransactionBatch batch)
    {
        if (!_batches.ContainsKey(batch.BatchId))
        {
            throw new KeyNotFoundException($"Batch with ID {batch.BatchId} not found");
        }

        _batches[batch.BatchId] = batch;
        return Task.FromResult(batch);
    }

    public Task<TransactionBatch> UpdateStatusAsync(string batchId, string newStatus)
    {
        if (!_batches.TryGetValue(batchId, out var batch))
        {
            throw new KeyNotFoundException($"Batch with ID {batchId} not found");
        }

        batch.Status = newStatus;
        if (newStatus == "Completed")
        {
            batch.ProcessedDate = DateTime.UtcNow;
        }

        return Task.FromResult(batch);
    }

    public Task<bool> DeleteAsync(string batchId)
    {
        return Task.FromResult(_batches.TryRemove(batchId, out _));
    }

    internal void Seed(TransactionBatch batch)
    {
        _batches.TryAdd(batch.BatchId, batch);
    }

    internal void Clear()
    {
        _batches.Clear();
    }
}
