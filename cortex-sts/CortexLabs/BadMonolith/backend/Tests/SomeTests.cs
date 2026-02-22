// ❌ SMELL-12: Tests that assert True — provide zero value
// These tests exist to inflate "test count" metrics without actually testing anything

using CortexLabs.FinTrack.Models;
using CortexLabs.FinTrack.Services;
using Xunit;

namespace CortexLabs.FinTrack.Tests;

// ❌ SMELL-12: Test class name doesn't match tested class
public class SomeTests
{
    // ❌ SMELL-12: Asserts true — always passes, tests nothing
    [Fact]
    public void Test1()
    {
        Assert.True(true);
    }

    // ❌ SMELL-12: Asserts true with misleading name
    [Fact]
    public void UserService_Should_Work()
    {
        Assert.True(1 == 1);
    }

    // ❌ SMELL-12: Tests implementation detail, not behavior
    [Fact]
    public void Transaction_Has_Properties()
    {
        var tx = new Transaction();
        Assert.NotNull(tx);
        // Only checks object creation — no actual behavior tested
    }

    // ❌ SMELL-12: Test with no assertions
    [Fact]
    public void Account_Balance_Test()
    {
        var account = new Account();
        account.Balance = 100.00m;
        // No assertion at all!
    }

    // ❌ SMELL-12: Misleading test — name says "validates" but doesn't
    [Fact]
    public void Should_Validate_Email_Format()
    {
        var service = new UserService();
        // Calls the method but doesn't check the result!
        service.ValidateEmail("test@test.com");
        Assert.True(true); // Always passes regardless of ValidateEmail result
    }

    // ❌ SMELL-12: Tests a method that doesn't exist anymore
    [Fact]
    public void Legacy_Import_Test()
    {
        // This test was written for a feature that was removed in Q2 2023
        // Nobody deleted the test
        Assert.True(true);
    }

    // ❌ SMELL-12: Duplicate of another test
    [Fact]
    public void Another_User_Test()
    {
        Assert.True(1 == 1); // Exact duplicate of UserService_Should_Work
    }

    // ❌ SMELL-12: Test that mocks everything — tests the mock, not the code
    [Fact]
    public void Transaction_Categorization_Works()
    {
        // In a real test, you'd call CategorizeTransaction and check the result
        // This test mocks the entire service and then asserts the mock returns what it was told to
        var expectedCategory = "food";
        Assert.Equal("food", expectedCategory); // ❌ Tautology!
    }
}

// ❌ SMELL-12: Entirely empty test class
public class AccountTests
{
    // TODO: Add tests (this TODO has been here since 2022)
}

// ❌ SMELL-12: Test class with only skipped tests
public class ReportTests
{
    [Fact(Skip = "Broken since Q1 2023")]
    public void Report_Generation_Test()
    {
        Assert.True(false); // Would fail if not skipped
    }

    [Fact(Skip = "Need to fix database connection")]
    public void Report_Export_Test()
    {
        throw new NotImplementedException();
    }
}

// ❌ SMELL-12: Integration test masquerading as unit test
public class DatabaseTests
{
    [Fact]
    public void Can_Connect_To_Database()
    {
        // ❌ Hits real database in unit test project — should be integration test
        try
        {
            // This will fail in CI because there's no database
            Assert.True(true); // Catches and silently passes
        }
        catch
        {
            Assert.True(true); // Even the catch passes!
        }
    }
}
