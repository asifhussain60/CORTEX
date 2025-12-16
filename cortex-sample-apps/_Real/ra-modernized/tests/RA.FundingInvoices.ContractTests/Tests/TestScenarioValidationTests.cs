using System.Text.Json;
using FluentAssertions;
using Xunit;

namespace RA.FundingInvoices.ContractTests.Tests;

/// <summary>
/// Validates test scenario JSON schema and structure
/// </summary>
public class TestScenarioValidationTests
{
    [Fact]
    public void TestScenariosJson_IsValidJson()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");

        // Act
        var jsonContent = File.ReadAllText(jsonPath);
        var action = () => JsonDocument.Parse(jsonContent);

        // Assert
        action.Should().NotThrow<JsonException>("test-scenarios.json must be valid JSON");
    }

    [Fact]
    public void TestScenariosJson_HasRequiredProperties()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");
        var jsonContent = File.ReadAllText(jsonPath);

        // Act
        using var document = JsonDocument.Parse(jsonContent);
        var root = document.RootElement;

        // Assert
        root.TryGetProperty("version", out _).Should().BeTrue("version property is required");
        root.TryGetProperty("description", out _).Should().BeTrue("description property is required");
        root.TryGetProperty("totalScenarios", out _).Should().BeTrue("totalScenarios property is required");
        root.TryGetProperty("categories", out _).Should().BeTrue("categories property is required");
    }

    [Fact]
    public void TestScenariosJson_HasCorrectScenarioCount()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");
        var jsonContent = File.ReadAllText(jsonPath);

        // Act
        using var document = JsonDocument.Parse(jsonContent);
        var root = document.RootElement;
        var totalScenarios = root.GetProperty("totalScenarios").GetInt32();

        // Assert
        totalScenarios.Should().Be(105, "test-scenarios.json should have 105 total scenarios");
    }

    [Fact]
    public void TestScenariosJson_HasAllWcfTransactions()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");
        var jsonContent = File.ReadAllText(jsonPath);
        var expectedTransactions = new[]
        {
            "XAddFundingInvoice",
            "XGenerateFundingInvoice",
            "Updater_CreateRAFundingInvoices",
            "XCloseFundingBatch",
            "XUpdateFundingBatch"
        };

        // Act
        using var document = JsonDocument.Parse(jsonContent);
        var categories = document.RootElement.GetProperty("categories");

        // Assert
        foreach (var transaction in expectedTransactions)
        {
            categories.TryGetProperty(transaction, out _).Should().BeTrue(
                $"categories should include {transaction}");
        }
    }

    [Fact]
    public void TestScenariosJson_AllScenariosHaveRequiredFields()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");
        var jsonContent = File.ReadAllText(jsonPath);

        // Act
        using var document = JsonDocument.Parse(jsonContent);
        var categories = document.RootElement.GetProperty("categories");

        // Assert
        foreach (var category in categories.EnumerateObject())
        {
            var categoryName = category.Name;
            var scenarios = category.Value;

            if (scenarios.TryGetProperty("happyPath", out var happyPath))
            {
                ValidateScenarioArray(happyPath, categoryName, "happyPath");
            }

            if (scenarios.TryGetProperty("errorCases", out var errorCases))
            {
                ValidateScenarioArray(errorCases, categoryName, "errorCases");
            }

            if (scenarios.TryGetProperty("edgeCases", out var edgeCases))
            {
                ValidateScenarioArray(edgeCases, categoryName, "edgeCases");
            }

            if (scenarios.TryGetProperty("boundaryConditions", out var boundary))
            {
                ValidateScenarioArray(boundary, categoryName, "boundaryConditions");
            }

            if (scenarios.TryGetProperty("stateTransitions", out var state))
            {
                ValidateScenarioArray(state, categoryName, "stateTransitions");
            }
        }
    }

    private void ValidateScenarioArray(JsonElement scenarios, string category, string type)
    {
        foreach (var scenario in scenarios.EnumerateArray())
        {
            scenario.TryGetProperty("id", out _).Should().BeTrue(
                $"{category}.{type} scenarios must have 'id' property");

            scenario.TryGetProperty("description", out _).Should().BeTrue(
                $"{category}.{type} scenarios must have 'description' property");

            scenario.TryGetProperty("request", out _).Should().BeTrue(
                $"{category}.{type} scenarios must have 'request' property");

            scenario.TryGetProperty("expectedResponse", out _).Should().BeTrue(
                $"{category}.{type} scenarios must have 'expectedResponse' property");
        }
    }

    [Fact]
    public void TestScenariosJson_PerformanceBaselinesExist()
    {
        // Arrange
        var jsonPath = Path.Combine(AppContext.BaseDirectory, "TestScenarios", "test-scenarios.json");
        var jsonContent = File.ReadAllText(jsonPath);

        // Act
        using var document = JsonDocument.Parse(jsonContent);
        var root = document.RootElement;

        // Assert
        root.TryGetProperty("performanceBaselines", out var baselines).Should().BeTrue(
            "test-scenarios.json should include performanceBaselines");

        baselines.GetArrayLength().Should().BeGreaterOrEqualTo(3,
            "should have at least 3 performance baseline scenarios");
    }
}
