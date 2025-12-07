using FluentAssertions;
using Xunit;
using Cortex.Clean.Domain.Entities;
using Cortex.Clean.Domain.Exceptions;

namespace Cortex.Clean.Tests.Domain;

/// <summary>
/// Tests for Task entity validation rules.
/// Following TDD: These tests will FAIL until we implement the Task entity.
/// </summary>
public class TaskEntityTests
{
    [Fact]
    public void Task_ShouldCreateSuccessfully_WhenValidDataProvided()
    {
        // Arrange
        var title = "Test Task";

        // Act
        var task = new TaskEntity(title);

        // Assert
        task.Should().NotBeNull();
        task.Title.Should().Be(title);
        task.IsCompleted.Should().BeFalse();
        task.Id.Should().BeGreaterThan(0);
    }

    [Fact]
    public void Task_ShouldThrowException_WhenTitleIsNull()
    {
        // Arrange
        string? title = null;

        // Act
        Action act = () => new TaskEntity(title!);

        // Assert
        act.Should().Throw<InvalidTaskException>()
            .WithMessage("*title*required*");
    }

    [Fact]
    public void Task_ShouldThrowException_WhenTitleIsEmpty()
    {
        // Arrange
        var title = string.Empty;

        // Act
        Action act = () => new TaskEntity(title);

        // Assert
        act.Should().Throw<InvalidTaskException>()
            .WithMessage("*title*required*");
    }

    [Fact]
    public void Task_ShouldThrowException_WhenTitleExceeds255Characters()
    {
        // Arrange
        var title = new string('A', 256);

        // Act
        Action act = () => new TaskEntity(title);

        // Assert
        act.Should().Throw<InvalidTaskException>()
            .WithMessage("*255*characters*");
    }

    [Fact]
    public void Task_ShouldToggleCompletion_WhenToggleCalled()
    {
        // Arrange
        var task = new TaskEntity("Test Task");
        var initialState = task.IsCompleted;

        // Act
        task.ToggleCompletion();

        // Assert
        task.IsCompleted.Should().Be(!initialState);
    }

    [Fact]
    public void Task_ShouldUpdateTitle_WhenValidTitleProvided()
    {
        // Arrange
        var task = new TaskEntity("Old Title");
        var newTitle = "New Title";

        // Act
        task.UpdateTitle(newTitle);

        // Assert
        task.Title.Should().Be(newTitle);
    }

    [Fact]
    public void Task_ShouldThrowException_WhenUpdatingWithInvalidTitle()
    {
        // Arrange
        var task = new TaskEntity("Valid Title");

        // Act
        Action act = () => task.UpdateTitle(string.Empty);

        // Assert
        act.Should().Throw<InvalidTaskException>();
    }

    [Theory]
    [InlineData("   ")]
    [InlineData("\t")]
    [InlineData("\n")]
    public void Task_ShouldThrowException_WhenTitleIsWhitespace(string title)
    {
        // Act
        Action act = () => new TaskEntity(title);

        // Assert
        act.Should().Throw<InvalidTaskException>()
            .WithMessage("*title*required*");
    }
}
