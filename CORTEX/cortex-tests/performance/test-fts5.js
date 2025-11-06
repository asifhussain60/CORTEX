// Quick FTS5 test for custom sql.js build
const initSqlJs = require('sql.js');
const path = require('path');

async function testFTS5() {
    console.log('🧪 Testing Custom sql.js FTS5 Support');
    console.log('=' .repeat(60));
    
    try {
        // Load custom sql.js
        const SQL = await initSqlJs({
            locateFile: (file) => path.join(__dirname, '../../node_modules/sql.js/dist/', file)
        });
        
        console.log('✅ sql.js loaded');
        
        // Create database
        const db = new SQL.Database();
        
        // Try to create FTS5 table
        console.log('\n📝 Creating FTS5 virtual table...');
        db.run(`
            CREATE VIRTUAL TABLE test_fts USING fts5(
                content,
                tags
            )
        `);
        
        console.log('✅ FTS5 table created successfully!');
        
        // Insert test data
        db.run("INSERT INTO test_fts (content, tags) VALUES ('authentication with JWT', 'security auth')");
        db.run("INSERT INTO test_fts (content, tags) VALUES ('database optimization tips', 'performance db')");
        db.run("INSERT INTO test_fts (content, tags) VALUES ('REST API authentication', 'api security')");
        
        console.log('✅ Test data inserted');
        
        // Query with FTS5
        console.log('\n🔍 Testing FTS5 MATCH query...');
        const result = db.exec("SELECT * FROM test_fts WHERE test_fts MATCH 'authentication'");
        
        console.log('✅ FTS5 query executed');
        console.log(`Found ${result[0].values.length} results`);
        console.log('Results:', result[0].values);
        
        db.close();
        
        console.log('\n' + '='.repeat(60));
        console.log('🎉 SUCCESS: Custom sql.js has FTS5 support!');
        console.log('=' .repeat(60));
        
    } catch (error) {
        console.error('\n❌ ERROR:', error.message);
        console.error('\n🚨 FTS5 is NOT available in this build');
        process.exit(1);
    }
}

testFTS5();
