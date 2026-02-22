namespace CortexLabs.FinTrack.Application.DTOs;

/// <summary>
/// Standard paginated response wrapper — fixes SMELL-20 (no pagination)
/// and provides consistent API envelope.
/// </summary>
/// <typeparam name="T">The DTO type contained in the page.</typeparam>
public class PagedResponse<T>
{
    public IReadOnlyList<T> Items { get; set; } = Array.Empty<T>();
    public int Page { get; set; }
    public int PageSize { get; set; }
    public int TotalCount { get; set; }
    public int TotalPages => (int)Math.Ceiling((double)TotalCount / PageSize);
    public bool HasNextPage => Page < TotalPages;
    public bool HasPreviousPage => Page > 1;
}
