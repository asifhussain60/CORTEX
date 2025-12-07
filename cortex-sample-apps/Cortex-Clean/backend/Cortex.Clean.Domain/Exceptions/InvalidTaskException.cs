namespace Cortex.Clean.Domain.Exceptions;

/// <summary>
/// Exception thrown when task validation fails.
/// </summary>
public class InvalidTaskException : Exception
{
    public InvalidTaskException(string message) : base(message)
    {
    }
}
