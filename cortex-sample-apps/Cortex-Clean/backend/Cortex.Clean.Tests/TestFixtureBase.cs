using AutoFixture;
using AutoFixture.Xunit2;

namespace Cortex.Clean.Tests;

/// <summary>
/// Base test fixture providing common test setup and utilities.
/// </summary>
public class TestFixtureBase
{
    protected readonly IFixture Fixture;

    public TestFixtureBase()
    {
        Fixture = new Fixture();
    }
}

/// <summary>
/// AutoFixture data attribute for xUnit tests.
/// </summary>
public class AutoMoqDataAttribute : AutoDataAttribute
{
    public AutoMoqDataAttribute()
        : base(() => new Fixture())
    {
    }
}
