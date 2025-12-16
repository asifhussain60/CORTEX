# Application Insights Kusto Queries for PaymentProcessor Transaction Invoices Monitoring

This document contains pre-built Kusto (KQL) queries for monitoring PaymentProcessor Transaction Invoices migration.

---

## 📊 Real-Time Metrics

### Current Error Rate (Last 5 Minutes)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    FailedRequests = countif(success == false)
| extend ErrorRatePercent = (FailedRequests * 100.0) / TotalRequests
| project ErrorRatePercent, TotalRequests, FailedRequests
```

### Current Success Rate (Last 5 Minutes)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true)
| extend SuccessRatePercent = (SuccessfulRequests * 100.0) / TotalRequests
| project SuccessRatePercent, TotalRequests, SuccessfulRequests
```

### Current Latency Metrics (Last 5 Minutes)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    AvgLatencyMs = avg(duration),
    P50LatencyMs = percentile(duration, 50),
    P95LatencyMs = percentile(duration, 95),
    P99LatencyMs = percentile(duration, 99),
    MaxLatencyMs = max(duration)
| project AvgLatencyMs, P50LatencyMs, P95LatencyMs, P99LatencyMs, MaxLatencyMs
```

---

## 🔍 Traffic Distribution Analysis

### Requests by Data Layer (Last 1 Hour)
```kusto
customMetrics
| where timestamp > ago(1h)
| where name == "DataLayer.RequestCount"
| extend DataLayer = tostring(customDimensions.DataLayer)
| summarize RequestCount = sum(value) by DataLayer
| extend Percentage = (RequestCount * 100.0) / toscalar(sum(RequestCount))
| project DataLayer, RequestCount, Percentage
| order by RequestCount desc
```

### Traffic Distribution Over Time (Last 24 Hours)
```kusto
customMetrics
| where timestamp > ago(24h)
| where name == "DataLayer.RequestCount"
| extend DataLayer = tostring(customDimensions.DataLayer)
| summarize RequestCount = sum(value) by bin(timestamp, 1h), DataLayer
| render timechart with (title="Traffic Distribution - Mock vs EF Core")
```

---

## ⚠️ Error Monitoring

### Top 10 Errors (Last 1 Hour)
```kusto
exceptions
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    ErrorCount = count(),
    SampleMessage = any(outerMessage),
    SampleStackTrace = any(details[0].parsedStack[0].assembly)
    by type
| order by ErrorCount desc
| take 10
```

### Failed Requests by Operation (Last 1 Hour)
```kusto
requests
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| where success == false
| summarize 
    FailureCount = count(),
    SampleUrl = any(url),
    AvgDuration = avg(duration)
    by operation_Name, resultCode
| order by FailureCount desc
```

### Exception Details (Last 30 Minutes)
```kusto
exceptions
| where timestamp > ago(30m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| extend DataLayer = tostring(customDimensions.DataLayer)
| project 
    timestamp,
    type,
    outerMessage,
    DataLayer,
    operation_Name,
    problemId
| order by timestamp desc
| take 50
```

---

## 📈 Performance Trends

### Latency Trend (Last 24 Hours)
```kusto
requests
| where timestamp > ago(24h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    AvgLatency = avg(duration),
    P95Latency = percentile(duration, 95)
    by bin(timestamp, 1h)
| render timechart with (title="Latency Trend - Average and P95")
```

### Request Volume Trend (Last 7 Days)
```kusto
requests
| where timestamp > ago(7d)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize RequestCount = count() by bin(timestamp, 1h)
| render timechart with (title="Request Volume - Last 7 Days")
```

### Success vs Failure Rate Trend (Last 24 Hours)
```kusto
requests
| where timestamp > ago(24h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true),
    FailedRequests = countif(success == false)
    by bin(timestamp, 5m)
| extend 
    SuccessRate = (SuccessfulRequests * 100.0) / TotalRequests,
    ErrorRate = (FailedRequests * 100.0) / TotalRequests
| project timestamp, SuccessRate, ErrorRate
| render timechart with (title="Success vs Error Rate")
```

---

## 🎯 Data Layer Comparison

### Mock vs EF Core Performance (Last 1 Hour)
```kusto
customMetrics
| where timestamp > ago(1h)
| where name in ("DataLayer.AvgLatency", "DataLayer.SuccessRate", "DataLayer.ErrorRate")
| extend DataLayer = tostring(customDimensions.DataLayer)
| summarize 
    AvgValue = avg(value)
    by name, DataLayer
| evaluate pivot(DataLayer)
```

### Mock vs EF Core Error Comparison (Last 1 Hour)
```kusto
exceptions
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| extend DataLayer = tostring(customDimensions.DataLayer)
| summarize ErrorCount = count() by DataLayer
| extend Percentage = (ErrorCount * 100.0) / toscalar(sum(ErrorCount))
| project DataLayer, ErrorCount, Percentage
```

---

## 🚨 Rollback Alerts

### Threshold Violations (Last 10 Minutes)
```kusto
let ErrorThreshold = 0.1; // 0.1%
let LatencyThreshold = 200; // 200ms
let SuccessThreshold = 99.9; // 99.9%
requests
| where timestamp > ago(10m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    FailedRequests = countif(success == false),
    AvgLatency = avg(duration)
| extend 
    ErrorRate = (FailedRequests * 100.0) / TotalRequests,
    SuccessRate = ((TotalRequests - FailedRequests) * 100.0) / TotalRequests
| extend 
    ErrorViolation = ErrorRate > ErrorThreshold,
    LatencyViolation = AvgLatency > LatencyThreshold,
    SuccessViolation = SuccessRate < SuccessThreshold
| project 
    TotalRequests,
    ErrorRate,
    AvgLatency,
    SuccessRate,
    ErrorViolation,
    LatencyViolation,
    SuccessViolation
```

### Circuit Breaker Events (Last 1 Hour)
```kusto
customEvents
| where timestamp > ago(1h)
| where name == "CircuitBreakerStateChange"
| extend 
    FromState = tostring(customDimensions.FromState),
    ToState = tostring(customDimensions.ToState),
    Reason = tostring(customDimensions.Reason)
| project timestamp, FromState, ToState, Reason
| order by timestamp desc
```

### Rollback Events (Last 24 Hours)
```kusto
customEvents
| where timestamp > ago(24h)
| where name == "EmergencyRollback"
| extend 
    Reason = tostring(customDimensions.Reason),
    FromPercentage = toint(customDimensions.FromPercentage),
    ToPercentage = toint(customDimensions.ToPercentage)
| project timestamp, Reason, FromPercentage, ToPercentage
| order by timestamp desc
```

---

## 📊 Business Metrics

### Requests by Operation (Last 1 Hour)
```kusto
requests
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    RequestCount = count(),
    AvgDuration = avg(duration),
    SuccessCount = countif(success == true),
    FailureCount = countif(success == false)
    by operation_Name
| extend SuccessRate = (SuccessCount * 100.0) / RequestCount
| order by RequestCount desc
```

### Top 10 Slowest Operations (Last 1 Hour)
```kusto
requests
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    RequestCount = count(),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95)
    by operation_Name
| order by P95Duration desc
| take 10
```

### User Activity (Last 24 Hours)
```kusto
requests
| where timestamp > ago(24h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| extend UserId = tostring(customDimensions.UserId)
| where isnotempty(UserId)
| summarize 
    RequestCount = count(),
    UniqueUsers = dcount(UserId)
| project RequestCount, UniqueUsers
```

---

## 🔧 Diagnostic Queries

### Slow Requests (>500ms, Last 1 Hour)
```kusto
requests
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| where duration > 500
| extend DataLayer = tostring(customDimensions.DataLayer)
| project 
    timestamp,
    operation_Name,
    url,
    duration,
    DataLayer,
    resultCode
| order by duration desc
| take 50
```

### Database Connection Pool Metrics (Last 1 Hour)
```kusto
customMetrics
| where timestamp > ago(1h)
| where name in ("ConnectionPool.Active", "ConnectionPool.Idle", "ConnectionPool.Total")
| summarize 
    AvgValue = avg(value),
    MaxValue = max(value)
    by name
| order by name
```

### Dependency Calls (Last 1 Hour)
```kusto
dependencies
| where timestamp > ago(1h)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    CallCount = count(),
    AvgDuration = avg(duration),
    SuccessCount = countif(success == true),
    FailureCount = countif(success == false)
    by type, name
| extend SuccessRate = (SuccessCount * 100.0) / CallCount
| order by CallCount desc
```

---

## 📅 Historical Analysis

### Daily Success Rate (Last 30 Days)
```kusto
requests
| where timestamp > ago(30d)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true)
    by bin(timestamp, 1d)
| extend SuccessRate = (SuccessfulRequests * 100.0) / TotalRequests
| project timestamp, SuccessRate
| render timechart with (title="Daily Success Rate - Last 30 Days")
```

### Weekly Request Volume (Last 12 Weeks)
```kusto
requests
| where timestamp > ago(84d)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize RequestCount = count() by bin(timestamp, 7d)
| render timechart with (title="Weekly Request Volume")
```

---

## 🎯 Migration Progress Tracking

### Feature Flag Percentage Changes (Last 30 Days)
```kusto
customEvents
| where timestamp > ago(30d)
| where name == "FeatureFlagUpdate"
| extend 
    FeatureName = tostring(customDimensions.FeatureName),
    Percentage = toint(customDimensions.Percentage)
| where FeatureName == "DataLayerRollout"
| project timestamp, Percentage
| render timechart with (title="EF Core Traffic Percentage - Migration Progress")
```

### Migration Milestone Events
```kusto
customEvents
| where timestamp > ago(90d)
| where name in ("MigrationStart", "MigrationPhaseComplete", "MigrationComplete")
| extend 
    Phase = tostring(customDimensions.Phase),
    Percentage = tostring(customDimensions.Percentage)
| project timestamp, name, Phase, Percentage
| order by timestamp desc
```

---

## 📋 Alert Query Templates

### Error Rate Alert (>0.1%)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    FailedRequests = countif(success == false)
| extend ErrorRate = (FailedRequests * 100.0) / TotalRequests
| where ErrorRate > 0.1
| project ErrorRate, TotalRequests, FailedRequests
```

### Latency Alert (>200ms)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize AvgLatency = avg(duration)
| where AvgLatency > 200
| project AvgLatency
```

### Success Rate Alert (<99.9%)
```kusto
requests
| where timestamp > ago(5m)
| where cloud_RoleName == "ra-transaction-invoices-api"
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true)
| extend SuccessRate = (SuccessfulRequests * 100.0) / TotalRequests
| where SuccessRate < 99.9
| project SuccessRate, TotalRequests, SuccessfulRequests
```

---

**Last Updated:** December 12, 2025  
**Maintained By:** Platform Engineering Team
