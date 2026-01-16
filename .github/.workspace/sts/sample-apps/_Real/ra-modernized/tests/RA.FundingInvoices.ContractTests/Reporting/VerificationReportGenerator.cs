using System.Text;
using System.Text.Json;

namespace RA.FundingInvoices.ContractTests.Reporting;

/// <summary>
/// Generates comprehensive verification reports in HTML, PDF, and JSON formats.
/// </summary>
public class VerificationReportGenerator
{
    private readonly VerificationReport _report;

    public VerificationReportGenerator(VerificationReport report)
    {
        _report = report;
    }

    public async Task GenerateAllReportsAsync(string outputDirectory)
    {
        Directory.CreateDirectory(outputDirectory);

        // Generate all report formats
        await GenerateHtmlReportAsync(Path.Combine(outputDirectory, "verification-report.html"));
        await GenerateJsonReportAsync(Path.Combine(outputDirectory, "verification-data.json"));
        await GenerateMarkdownSummaryAsync(Path.Combine(outputDirectory, "verification-summary.md"));
    }

    public async Task GenerateHtmlReportAsync(string outputPath)
    {
        var html = new StringBuilder();

        // HTML Header
        html.AppendLine("<!DOCTYPE html>");
        html.AppendLine("<html lang=\"en\">");
        html.AppendLine("<head>");
        html.AppendLine("    <meta charset=\"UTF-8\">");
        html.AppendLine("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">");
        html.AppendLine("    <title>Phase 4a - Contract Verification Report</title>");
        html.AppendLine("    <style>");
        html.AppendLine(GetCssStyles());
        html.AppendLine("    </style>");
        html.AppendLine("</head>");
        html.AppendLine("<body>");

        // Executive Summary
        html.AppendLine(GenerateExecutiveSummary());

        // Gate Status
        html.AppendLine(GenerateGateStatus());

        // Match Rate Visualization
        html.AppendLine(GenerateMatchRateVisualization());

        // Discrepancy Breakdown
        html.AppendLine(GenerateDiscrepancyBreakdown());

        // Performance Comparison
        html.AppendLine(GeneratePerformanceComparison());

        // Detailed Results
        html.AppendLine(GenerateDetailedResults());

        // Stakeholder Sign-off
        html.AppendLine(GenerateSignOffSection());

        html.AppendLine("</body>");
        html.AppendLine("</html>");

        await File.WriteAllTextAsync(outputPath, html.ToString());
    }

    private string GetCssStyles()
    {
        return @"
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-pass {
            background-color: #27ae60;
            color: white;
        }
        .status-fail {
            background-color: #e74c3c;
            color: white;
        }
        .metric-card {
            display: inline-block;
            width: 200px;
            margin: 10px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-label {
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        .severity-critical {
            background-color: #e74c3c;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .severity-high {
            background-color: #e67e22;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .severity-medium {
            background-color: #f39c12;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .severity-low {
            background-color: #95a5a6;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .match {
            color: #27ae60;
            font-weight: bold;
        }
        .mismatch {
            color: #e74c3c;
            font-weight: bold;
        }
        .sign-off {
            margin-top: 40px;
            padding: 20px;
            border: 2px solid #3498db;
            background-color: #ecf0f1;
        }
        .signature-line {
            margin-top: 30px;
            border-top: 1px solid #000;
            padding-top: 5px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background-color: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: #27ae60;
            text-align: center;
            line-height: 30px;
            color: white;
            font-weight: bold;
        }
        ";
    }

    private string GenerateExecutiveSummary()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h1>Phase 4a - WCF to REST Contract Verification Report</h1>");
        sb.AppendLine($"    <p><strong>Report Date:</strong> {DateTime.Now:MMMM dd, yyyy HH:mm:ss}</p>");
        sb.AppendLine($"    <p><strong>Migration Project:</strong> RA Funding Invoices (Product.RA.Api)</p>");
        sb.AppendLine($"    <p><strong>Verification Duration:</strong> {_report.Duration:hh\\:mm\\:ss}</p>");
        sb.AppendLine();
        sb.AppendLine("    <h2>Executive Summary</h2>");
        sb.AppendLine("    <p>");
        sb.AppendLine($"        This report documents the contract verification results for Phase 4a of the RA Funding Invoices migration.");
        sb.AppendLine($"        A total of <strong>{_report.TotalScenarios}</strong> test scenarios were executed to validate 100% parity between ");
        sb.AppendLine("        legacy WCF transactions and the modernized REST API.");
        sb.AppendLine("    </p>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GenerateGateStatus()
    {
        var sb = new StringBuilder();
        var statusClass = _report.IsPassingGate ? "status-pass" : "status-fail";
        var statusText = _report.IsPassingGate ? "✅ PASS" : "❌ FAIL";

        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h2>Gate Status");
        sb.AppendLine($"        <span class=\"status-badge {statusClass}\">{statusText}</span>");
        sb.AppendLine("    </h2>");
        sb.AppendLine();
        sb.AppendLine("    <div class=\"metric-card\">");
        sb.AppendLine($"        <div class=\"metric-value\">{_report.MatchRate:F1}%</div>");
        sb.AppendLine("        <div class=\"metric-label\">Match Rate</div>");
        sb.AppendLine("    </div>");
        sb.AppendLine();
        sb.AppendLine("    <div class=\"metric-card\">");
        sb.AppendLine($"        <div class=\"metric-value\">{_report.PassedScenarios}</div>");
        sb.AppendLine("        <div class=\"metric-label\">Passed</div>");
        sb.AppendLine("    </div>");
        sb.AppendLine();
        sb.AppendLine("    <div class=\"metric-card\">");
        sb.AppendLine($"        <div class=\"metric-value\">{_report.FailedScenarios}</div>");
        sb.AppendLine("        <div class=\"metric-label\">Failed</div>");
        sb.AppendLine("    </div>");
        sb.AppendLine();
        sb.AppendLine("    <div class=\"metric-card\">");
        sb.AppendLine($"        <div class=\"metric-value\">{_report.CriticalDiscrepancies}</div>");
        sb.AppendLine("        <div class=\"metric-label\">Critical Issues</div>");
        sb.AppendLine("    </div>");
        sb.AppendLine();
        sb.AppendLine("    <h3>Gate Requirements</h3>");
        sb.AppendLine("    <ul>");
        sb.AppendLine($"        <li class=\"{(_report.MatchRate == 100 ? "match" : "mismatch")}\">Match Rate: {_report.MatchRate:F1}% (Required: 100.0%)</li>");
        sb.AppendLine($"        <li class=\"{(_report.CriticalDiscrepancies == 0 ? "match" : "mismatch")}\">Critical Discrepancies: {_report.CriticalDiscrepancies} (Required: 0)</li>");
        sb.AppendLine($"        <li class=\"{(_report.IsPassingGate ? "match" : "mismatch")}\">Overall Gate Status: {(_report.IsPassingGate ? "PASS" : "FAIL")}</li>");
        sb.AppendLine("    </ul>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GenerateMatchRateVisualization()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h2>Match Rate Visualization</h2>");
        sb.AppendLine("    <div class=\"progress-bar\">");
        sb.AppendLine($"        <div class=\"progress-fill\" style=\"width: {_report.MatchRate}%\">{_report.MatchRate:F1}%</div>");
        sb.AppendLine("    </div>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GenerateDiscrepancyBreakdown()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h2>Discrepancy Breakdown</h2>");
        sb.AppendLine("    <table>");
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <th>Severity</th>");
        sb.AppendLine("            <th>Count</th>");
        sb.AppendLine("            <th>Percentage</th>");
        sb.AppendLine("        </tr>");

        var totalDiscrepancies = _report.CriticalDiscrepancies + _report.HighDiscrepancies + _report.MediumDiscrepancies;
        
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <td><span class=\"severity-critical\">Critical</span></td>");
        sb.AppendLine($"            <td>{_report.CriticalDiscrepancies}</td>");
        sb.AppendLine($"            <td>{(totalDiscrepancies > 0 ? (_report.CriticalDiscrepancies / (double)totalDiscrepancies * 100) : 0):F1}%</td>");
        sb.AppendLine("        </tr>");
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <td><span class=\"severity-high\">High</span></td>");
        sb.AppendLine($"            <td>{_report.HighDiscrepancies}</td>");
        sb.AppendLine($"            <td>{(totalDiscrepancies > 0 ? (_report.HighDiscrepancies / (double)totalDiscrepancies * 100) : 0):F1}%</td>");
        sb.AppendLine("        </tr>");
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <td><span class=\"severity-medium\">Medium</span></td>");
        sb.AppendLine($"            <td>{_report.MediumDiscrepancies}</td>");
        sb.AppendLine($"            <td>{(totalDiscrepancies > 0 ? (_report.MediumDiscrepancies / (double)totalDiscrepancies * 100) : 0):F1}%</td>");
        sb.AppendLine("        </tr>");
        sb.AppendLine("    </table>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GeneratePerformanceComparison()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h2>Performance Comparison</h2>");
        sb.AppendLine("    <table>");
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <th>WCF Transaction</th>");
        sb.AppendLine("            <th>WCF Avg (ms)</th>");
        sb.AppendLine("            <th>REST Avg (ms)</th>");
        sb.AppendLine("            <th>Difference</th>");
        sb.AppendLine("        </tr>");

        var groupedResults = _report.Results.GroupBy(r => r.WcfTransaction);
        foreach (var group in groupedResults)
        {
            var avgWcf = group.Average(r => r.WcfResponseTime);
            var avgRest = group.Average(r => r.RestResponseTime);
            var difference = avgRest - avgWcf;
            var percentDiff = avgWcf > 0 ? (difference / avgWcf * 100) : 0;

            sb.AppendLine("        <tr>");
            sb.AppendLine($"            <td>{group.Key}</td>");
            sb.AppendLine($"            <td>{avgWcf:F0}</td>");
            sb.AppendLine($"            <td>{avgRest:F0}</td>");
            sb.AppendLine($"            <td>{(difference >= 0 ? "+" : "")}{difference:F0} ms ({(percentDiff >= 0 ? "+" : "")}{percentDiff:F1}%)</td>");
            sb.AppendLine("        </tr>");
        }

        sb.AppendLine("    </table>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GenerateDetailedResults()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <h2>Detailed Test Results</h2>");
        sb.AppendLine("    <table>");
        sb.AppendLine("        <tr>");
        sb.AppendLine("            <th>Scenario ID</th>");
        sb.AppendLine("            <th>Description</th>");
        sb.AppendLine("            <th>Status</th>");
        sb.AppendLine("            <th>Discrepancies</th>");
        sb.AppendLine("        </tr>");

        foreach (var result in _report.Results)
        {
            var statusClass = result.IsMatch ? "match" : "mismatch";
            var statusText = result.IsMatch ? "✓ PASS" : "✗ FAIL";

            sb.AppendLine("        <tr>");
            sb.AppendLine($"            <td>{result.ScenarioId}</td>");
            sb.AppendLine($"            <td>{result.Description}</td>");
            sb.AppendLine($"            <td class=\"{statusClass}\">{statusText}</td>");
            sb.AppendLine($"            <td>{result.Discrepancies.Count}</td>");
            sb.AppendLine("        </tr>");

            if (result.Discrepancies.Any())
            {
                sb.AppendLine("        <tr>");
                sb.AppendLine("            <td colspan=\"4\">");
                sb.AppendLine("                <table style=\"margin: 10px; width: 95%;\">");
                sb.AppendLine("                    <tr>");
                sb.AppendLine("                        <th>Field</th>");
                sb.AppendLine("                        <th>WCF Value</th>");
                sb.AppendLine("                        <th>REST Value</th>");
                sb.AppendLine("                        <th>Severity</th>");
                sb.AppendLine("                    </tr>");

                foreach (var discrepancy in result.Discrepancies)
                {
                    var severityClass = $"severity-{discrepancy.Severity.ToString().ToLower()}";
                    sb.AppendLine("                    <tr>");
                    sb.AppendLine($"                        <td>{discrepancy.Field}</td>");
                    sb.AppendLine($"                        <td>{discrepancy.WcfValue}</td>");
                    sb.AppendLine($"                        <td>{discrepancy.RestValue}</td>");
                    sb.AppendLine($"                        <td><span class=\"{severityClass}\">{discrepancy.Severity}</span></td>");
                    sb.AppendLine("                    </tr>");
                }

                sb.AppendLine("                </table>");
                sb.AppendLine("            </td>");
                sb.AppendLine("        </tr>");
            }
        }

        sb.AppendLine("    </table>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    private string GenerateSignOffSection()
    {
        var sb = new StringBuilder();
        sb.AppendLine("<div class=\"container\">");
        sb.AppendLine("    <div class=\"sign-off\">");
        sb.AppendLine("        <h2>Stakeholder Sign-Off</h2>");
        sb.AppendLine("        <p>");
        sb.AppendLine("            I hereby acknowledge that I have reviewed this contract verification report and ");
        sb.AppendLine($"            {(_report.IsPassingGate ? "approve" : "reject")} the migration to proceed to Phase 5.");
        sb.AppendLine("        </p>");
        sb.AppendLine();
        sb.AppendLine("        <div class=\"signature-line\">");
        sb.AppendLine("            <strong>Product VP Signature:</strong> ___________________________ <strong>Date:</strong> ___________");
        sb.AppendLine("        </div>");
        sb.AppendLine();
        sb.AppendLine("        <div class=\"signature-line\">");
        sb.AppendLine("            <strong>Engineering Lead Signature:</strong> ___________________________ <strong>Date:</strong> ___________");
        sb.AppendLine("        </div>");
        sb.AppendLine();
        sb.AppendLine("        <div class=\"signature-line\">");
        sb.AppendLine("            <strong>QA Lead Signature:</strong> ___________________________ <strong>Date:</strong> ___________");
        sb.AppendLine("        </div>");
        sb.AppendLine("    </div>");
        sb.AppendLine("</div>");
        return sb.ToString();
    }

    public async Task GenerateJsonReportAsync(string outputPath)
    {
        var jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        var json = JsonSerializer.Serialize(_report, jsonOptions);
        await File.WriteAllTextAsync(outputPath, json);
    }

    public async Task GenerateMarkdownSummaryAsync(string outputPath)
    {
        var sb = new StringBuilder();

        sb.AppendLine("# Phase 4a - Contract Verification Summary");
        sb.AppendLine();
        sb.AppendLine($"**Report Date:** {DateTime.Now:MMMM dd, yyyy HH:mm:ss}  ");
        sb.AppendLine($"**Migration Project:** RA Funding Invoices (Product.RA.Api)  ");
        sb.AppendLine($"**Verification Duration:** {_report.Duration:hh\\:mm\\:ss}  ");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine();
        sb.AppendLine("## Gate Status");
        sb.AppendLine();
        sb.AppendLine($"**Overall:** {(_report.IsPassingGate ? "✅ PASS" : "❌ FAIL")}");
        sb.AppendLine();
        sb.AppendLine("| Metric | Value | Requirement | Status |");
        sb.AppendLine("|--------|-------|-------------|--------|");
        sb.AppendLine($"| Match Rate | {_report.MatchRate:F1}% | 100.0% | {(_report.MatchRate == 100 ? "✅" : "❌")} |");
        sb.AppendLine($"| Critical Discrepancies | {_report.CriticalDiscrepancies} | 0 | {(_report.CriticalDiscrepancies == 0 ? "✅" : "❌")} |");
        sb.AppendLine($"| Passed Scenarios | {_report.PassedScenarios}/{_report.TotalScenarios} | {_report.TotalScenarios}/{_report.TotalScenarios} | {(_report.PassedScenarios == _report.TotalScenarios ? "✅" : "❌")} |");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine();
        sb.AppendLine("## Discrepancy Breakdown");
        sb.AppendLine();
        sb.AppendLine("| Severity | Count |");
        sb.AppendLine("|----------|-------|");
        sb.AppendLine($"| Critical | {_report.CriticalDiscrepancies} |");
        sb.AppendLine($"| High | {_report.HighDiscrepancies} |");
        sb.AppendLine($"| Medium | {_report.MediumDiscrepancies} |");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine();
        sb.AppendLine("## Next Steps");
        sb.AppendLine();
        if (_report.IsPassingGate)
        {
            sb.AppendLine("✅ **Gate Passed** - Proceed to Phase 5 (Legacy Service Migration)");
            sb.AppendLine();
            sb.AppendLine("1. Obtain stakeholder sign-off");
            sb.AppendLine("2. Lock contract baseline (no changes without re-verification)");
            sb.AppendLine("3. Begin Phase 5 kickoff");
        }
        else
        {
            sb.AppendLine("❌ **Gate Failed** - Phase 5 blocked until issues resolved");
            sb.AppendLine();
            sb.AppendLine("**Required Actions:**");
            sb.AppendLine($"1. Fix {_report.CriticalDiscrepancies} critical discrepancies");
            sb.AppendLine($"2. Fix {_report.FailedScenarios} failed test scenarios");
            sb.AppendLine("3. Re-run verification");
            sb.AppendLine("4. Achieve 100% match rate");
        }

        await File.WriteAllTextAsync(outputPath, sb.ToString());
    }
}

// Supporting classes already defined in ContractVerificationEngine.cs
