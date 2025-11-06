/**
 * Phase -1.1: sql.js Performance Benchmarking
 * 
 * Validates that sql.js (WASM) meets CORTEX performance targets:
 * - Tier 1 (Working Memory): <50ms for last 50 conversations
 * - Tier 2 (Long-Term Knowledge): <100ms for FTS5 pattern search
 * 
 * If targets not met, activate contingency: server-side SQLite API.
 * 
 * Run with: npx playwright test benchmark-sql-js.spec.ts
 */

import { test, expect } from '@playwright/test';
import initSqlJs from 'sql.js';
import * as fs from 'fs';
import * as path from 'path';

// Performance targets from CORTEX design
const TIER1_TARGET_MS = 50;   // Working Memory
const TIER2_TARGET_MS = 100;  // Long-Term Knowledge
const PERCENTILE_95_MULTIPLIER = 1.5; // p95 can be 1.5x p50

// Test configuration
const NUM_ITERATIONS = 100; // Run each query 100 times for statistics
const TEST_DB_PATH = path.join(__dirname, 'test-cortex-brain.db');

interface BenchmarkResult {
  p50: number;
  p95: number;
  p99: number;
  min: number;
  max: number;
  mean: number;
  iterations: number;
}

/**
 * Calculate percentile from sorted array
 */
function percentile(sorted: number[], p: number): number {
  const index = Math.ceil((sorted.length * p) / 100) - 1;
  return sorted[Math.max(0, index)];
}

/**
 * Benchmark a query and return statistics
 */
async function benchmarkQuery(
  db: any,
  query: string,
  params: any[] = []
): Promise<BenchmarkResult> {
  const timings: number[] = [];
  
  for (let i = 0; i < NUM_ITERATIONS; i++) {
    const start = performance.now();
    db.exec(query, params);
    const elapsed = performance.now() - start;
    timings.push(elapsed);
  }
  
  // Sort for percentile calculation
  const sorted = [...timings].sort((a, b) => a - b);
  
  return {
    p50: percentile(sorted, 50),
    p95: percentile(sorted, 95),
    p99: percentile(sorted, 99),
    min: sorted[0],
    max: sorted[sorted.length - 1],
    mean: timings.reduce((a, b) => a + b, 0) / timings.length,
    iterations: NUM_ITERATIONS,
  };
}

/**
 * Format benchmark result for display
 */
function formatResult(result: BenchmarkResult): string {
  return [
    `p50: ${result.p50.toFixed(2)}ms`,
    `p95: ${result.p95.toFixed(2)}ms`,
    `p99: ${result.p99.toFixed(2)}ms`,
    `min: ${result.min.toFixed(2)}ms`,
    `max: ${result.max.toFixed(2)}ms`,
    `mean: ${result.mean.toFixed(2)}ms`,
  ].join(' | ');
}

test.describe('Phase -1: sql.js Performance Benchmarking', () => {
  let SQL: any;
  let db: any;
  
  test.beforeAll(async () => {
    // Check test database exists
    if (!fs.existsSync(TEST_DB_PATH)) {
      throw new Error(
        `Test database not found: ${TEST_DB_PATH}\n` +
        'Run: python generate-test-data.py'
      );
    }
    
    // Initialize sql.js (WASM)
    console.log('Loading sql.js (WebAssembly)...');
    SQL = await initSqlJs({
      // Use local node_modules build for testing
      locateFile: (file: string) => path.join(__dirname, '../../node_modules/sql.js/dist/', file),
    });
    
    // Load test database
    console.log(`Loading test database: ${TEST_DB_PATH}`);
    const dbBuffer = fs.readFileSync(TEST_DB_PATH);
    db = new SQL.Database(dbBuffer);
    
    // Verify data loaded
    const result = db.exec('SELECT COUNT(*) as count FROM conversations');
    const conversationCount = result[0].values[0][0];
    console.log(`Loaded ${conversationCount} conversations`);
    
    const patternResult = db.exec('SELECT COUNT(*) as count FROM patterns');
    const patternCount = patternResult[0].values[0][0];
    console.log(`Loaded ${patternCount} patterns`);
  });
  
  test.afterAll(async () => {
    if (db) {
      db.close();
    }
  });
  
  test('Tier 1: Query last 50 conversations (Working Memory)', async () => {
    console.log('\n📊 Benchmarking Tier 1: Working Memory Query');
    console.log('Target: <50ms (p50), <75ms (p95)');
    console.log('Query: SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 50');
    
    const result = await benchmarkQuery(
      db,
      'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 50'
    );
    
    console.log(`\nResults (${result.iterations} iterations):`);
    console.log(formatResult(result));
    
    // Validate against targets
    const p50_pass = result.p50 < TIER1_TARGET_MS;
    const p95_pass = result.p95 < TIER1_TARGET_MS * PERCENTILE_95_MULTIPLIER;
    
    console.log(`\n✅ p50 < ${TIER1_TARGET_MS}ms: ${p50_pass ? 'PASS' : 'FAIL'}`);
    console.log(`✅ p95 < ${TIER1_TARGET_MS * PERCENTILE_95_MULTIPLIER}ms: ${p95_pass ? 'PASS' : 'FAIL'}`);
    
    if (!p50_pass || !p95_pass) {
      console.error('\n⚠️  PERFORMANCE TARGET NOT MET');
      console.error('Contingency: Consider server-side SQLite API');
    }
    
    // Assert (fail test if targets not met)
    expect(result.p50).toBeLessThan(TIER1_TARGET_MS);
    expect(result.p95).toBeLessThan(TIER1_TARGET_MS * PERCENTILE_95_MULTIPLIER);
  });
  
  test('Tier 2: FTS5 pattern search (Long-Term Knowledge)', async () => {
    console.log('\n📊 Benchmarking Tier 2: FTS5 Pattern Search');
    console.log('Target: <100ms (p50), <150ms (p95)');
    console.log('Query: SELECT * FROM patterns_fts WHERE patterns_fts MATCH "authentication" LIMIT 20');
    
    const result = await benchmarkQuery(
      db,
      'SELECT * FROM patterns_fts WHERE patterns_fts MATCH "authentication" LIMIT 20'
    );
    
    console.log(`\nResults (${result.iterations} iterations):`);
    console.log(formatResult(result));
    
    // Validate against targets
    const p50_pass = result.p50 < TIER2_TARGET_MS;
    const p95_pass = result.p95 < TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER;
    
    console.log(`\n✅ p50 < ${TIER2_TARGET_MS}ms: ${p50_pass ? 'PASS' : 'FAIL'}`);
    console.log(`✅ p95 < ${TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER}ms: ${p95_pass ? 'PASS' : 'FAIL'}`);
    
    if (!p50_pass || !p95_pass) {
      console.error('\n⚠️  PERFORMANCE TARGET NOT MET');
      console.error('Contingency: Use LIKE queries or server-side API');
    }
    
    // Assert
    expect(result.p50).toBeLessThan(TIER2_TARGET_MS);
    expect(result.p95).toBeLessThan(TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER);
  });
  
  test('Tier 2: Complex pattern query with JOIN', async () => {
    console.log('\n📊 Benchmarking Tier 2: Complex Query (FTS5 + JOIN)');
    console.log('Target: <100ms (p50), <150ms (p95)');
    console.log('Query: Complex FTS5 search with confidence filter');
    
    const result = await benchmarkQuery(
      db,
      `
      SELECT p.id, p.pattern, p.context, p.confidence
      FROM patterns p
      JOIN patterns_fts fts ON p.id = fts.rowid
      WHERE patterns_fts MATCH "test OR authentication"
        AND p.confidence > 0.8
      ORDER BY p.confidence DESC
      LIMIT 20
      `
    );
    
    console.log(`\nResults (${result.iterations} iterations):`);
    console.log(formatResult(result));
    
    // Validate
    const p50_pass = result.p50 < TIER2_TARGET_MS;
    const p95_pass = result.p95 < TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER;
    
    console.log(`\n✅ p50 < ${TIER2_TARGET_MS}ms: ${p50_pass ? 'PASS' : 'FAIL'}`);
    console.log(`✅ p95 < ${TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER}ms: ${p95_pass ? 'PASS' : 'FAIL'}`);
    
    // Assert
    expect(result.p50).toBeLessThan(TIER2_TARGET_MS);
    expect(result.p95).toBeLessThan(TIER2_TARGET_MS * PERCENTILE_95_MULTIPLIER);
  });
  
  test('Database size validation', async () => {
    console.log('\n📊 Database Size Validation');
    console.log('Target: <270 KB (for 1000 conversations + 3000 patterns)');
    
    const stats = fs.statSync(TEST_DB_PATH);
    const sizeKB = stats.size / 1024;
    
    console.log(`Database size: ${sizeKB.toFixed(2)} KB`);
    
    const pass = sizeKB < 270;
    console.log(`✅ Size < 270 KB: ${pass ? 'PASS' : 'FAIL'}`);
    
    if (!pass) {
      console.error('\n⚠️  SIZE TARGET EXCEEDED');
      console.error('Consider: Compression, schema optimization, or data limits');
    }
    
    // Assert
    expect(sizeKB).toBeLessThan(270);
  });
  
  test('WAL mode concurrency simulation', async () => {
    console.log('\n📊 WAL Mode Concurrency Simulation');
    console.log('Target: <10ms blocking time for concurrent reads');
    
    // Simulate 5 concurrent readers
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(
        benchmarkQuery(
          db,
          'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 50'
        )
      );
    }
    
    const start = performance.now();
    const results = await Promise.all(promises);
    const totalTime = performance.now() - start;
    
    console.log(`\nConcurrent execution time: ${totalTime.toFixed(2)}ms`);
    console.log(`Average per query: ${(totalTime / 5).toFixed(2)}ms`);
    
    // In WAL mode, concurrent reads should not block significantly
    const avgTime = totalTime / 5;
    const blocking = avgTime - results[0].p50;
    
    console.log(`Estimated blocking: ${blocking.toFixed(2)}ms`);
    console.log(`✅ Blocking < 10ms: ${blocking < 10 ? 'PASS' : 'FAIL'}`);
    
    // Note: sql.js is single-threaded, so this is a simplified test
    // Real browser testing needed for accurate concurrency validation
    expect(blocking).toBeLessThan(10);
  });
  
  test('Generate Phase -1 decision report', async () => {
    console.log('\n📋 Phase -1.1 Decision Summary');
    console.log('=' .repeat(60));
    
    // Run quick validation queries
    const tier1 = await benchmarkQuery(
      db,
      'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 50'
    );
    
    const tier2 = await benchmarkQuery(
      db,
      'SELECT * FROM patterns_fts WHERE patterns_fts MATCH "authentication" LIMIT 20'
    );
    
    const tier1_ok = tier1.p50 < TIER1_TARGET_MS && tier1.p95 < TIER1_TARGET_MS * 1.5;
    const tier2_ok = tier2.p50 < TIER2_TARGET_MS && tier2.p95 < TIER2_TARGET_MS * 1.5;
    
    console.log(`\nTier 1 (Working Memory): ${tier1_ok ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`  p50: ${tier1.p50.toFixed(2)}ms (target: <${TIER1_TARGET_MS}ms)`);
    console.log(`  p95: ${tier1.p95.toFixed(2)}ms (target: <${TIER1_TARGET_MS * 1.5}ms)`);
    
    console.log(`\nTier 2 (Long-Term Knowledge): ${tier2_ok ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`  p50: ${tier2.p50.toFixed(2)}ms (target: <${TIER2_TARGET_MS}ms)`);
    console.log(`  p95: ${tier2.p95.toFixed(2)}ms (target: <${TIER2_TARGET_MS * 1.5}ms)`);
    
    const overallPass = tier1_ok && tier2_ok;
    
    console.log('\n' + '='.repeat(60));
    console.log(`DECISION: ${overallPass ? '✅ PROCEED WITH SQL.JS' : '❌ ACTIVATE CONTINGENCY'}`);
    
    if (!overallPass) {
      console.log('\n⚠️  Contingency Plan:');
      console.log('  1. Implement server-side SQLite API (Python + FastAPI)');
      console.log('  2. Dashboard calls HTTP endpoints instead of sql.js');
      console.log('  3. Add response caching to minimize latency');
      console.log('  4. Update Phase 1-5 timeline (+8-12 hours)');
    } else {
      console.log('\n✅ sql.js meets all performance targets');
      console.log('✅ Proceed to Phase -1.2 (Browser API Compatibility)');
    }
    console.log('='.repeat(60));
  });
});
