"""
CORTEX Tier 1 Utilization Monitor
Weekly brain health check script
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import yaml

def check_tier1_utilization():
    """Monitor Tier 1 conversation memory utilization and quality."""
    
    print("\n" + "="*70)
    print("   CORTEX TIER 1 UTILIZATION MONITOR")
    print("   " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # Load monitoring config
    config_path = Path('cortex-brain/operations/brain-monitoring.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        thresholds = config['tier1_health_thresholds']
    else:
        # Default thresholds
        thresholds = {
            'valid_conversation_rate': {'excellent': 90, 'good': 80, 'fair': 70},
            'quality_score_avg': {'excellent': 8.0, 'good': 6.0, 'fair': 4.0}
        }
    
    # Connect to Tier 1 database
    db_path = Path('cortex-brain/tier1-working-memory.db')
    if not db_path.exists():
        print("❌ Tier 1 database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get conversation statistics
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_convs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE message_count > 0')
    valid_convs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE message_count = 0')
    empty_convs = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT AVG(quality_score), MIN(quality_score), MAX(quality_score)
        FROM conversations
        WHERE message_count > 0 AND quality_score > 0
    ''')
    quality_stats = cursor.fetchone()
    avg_quality = quality_stats[0] if quality_stats[0] else 0
    min_quality = quality_stats[1] if quality_stats[1] else 0
    max_quality = quality_stats[2] if quality_stats[2] else 0
    
    # Data validation - check for NULL titles
    cursor.execute('''\n        SELECT COUNT(*) FROM conversations WHERE title IS NULL\n    ''')
    null_titles = cursor.fetchone()[0]
    
    # Calculate metrics
    valid_rate = (valid_convs / total_convs * 100) if total_convs > 0 else 0
    fifo_capacity = 70  # From config
    utilization = (total_convs / fifo_capacity * 100) if fifo_capacity > 0 else 0
    
    # Determine health status
    if valid_rate >= thresholds['valid_conversation_rate']['excellent']:
        valid_status = "✅ EXCELLENT"
    elif valid_rate >= thresholds['valid_conversation_rate']['good']:
        valid_status = "✅ GOOD"
    elif valid_rate >= thresholds['valid_conversation_rate']['fair']:
        valid_status = "⚠️ FAIR"
    else:
        valid_status = "❌ POOR"
    
    if avg_quality >= thresholds['quality_score_avg']['excellent']:
        quality_status = "✅ EXCELLENT"
    elif avg_quality >= thresholds['quality_score_avg']['good']:
        quality_status = "✅ GOOD"
    elif avg_quality >= thresholds['quality_score_avg']['fair']:
        quality_status = "⚠️ FAIR"
    else:
        quality_status = "❌ POOR"
    
    # Display metrics
    print("\n📊 CONVERSATION METRICS")
    print(f"   Total Conversations: {total_convs}")
    print(f"   Valid Conversations: {valid_convs} ({valid_rate:.1f}%)")
    print(f"   Empty Conversations: {empty_convs} ({empty_convs/total_convs*100:.1f}%)")
    print(f"   Status: {valid_status}")
    
    print("\n📈 QUALITY METRICS")
    print(f"   Average Quality: {avg_quality:.1f}/10")
    print(f"   Min Quality: {min_quality:.1f}/10")
    print(f"   Max Quality: {max_quality:.1f}/10")
    print(f"   Status: {quality_status}")
    
    print("\n💾 CAPACITY")
    print(f"   FIFO Capacity: {fifo_capacity} conversations")
    print(f"   Current Usage: {total_convs}/{fifo_capacity} ({utilization:.1f}%)")
    
    if utilization >= 70:
        capacity_status = "⚠️ HIGH - Consider cleanup"
    elif utilization >= 50:
        capacity_status = "✅ OPTIMAL"
    else:
        capacity_status = "ℹ️ LOW - Room for growth"
    print(f"   Status: {capacity_status}")
    
    # Recent imports
    print("\n🕐 RECENT ACTIVITY (Last 5 Valid Imports)")
    cursor.execute('''
        SELECT conversation_id, title, message_count, quality_score, created_at
        FROM conversations
        WHERE message_count > 0
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    recent = cursor.fetchall()
    if recent:
        for i, (conv_id, title, msg_count, quality, created) in enumerate(recent, 1):
            print(f"   {i}. {title[:50]}")
            print(f"      Quality: {quality:.1f}/10 | Messages: {msg_count} | {created[:10]}")
    else:
        print("   No recent imports found")
    
    # Alerts
    alerts = []
    if valid_rate < 70:
        alerts.append(f"⚠️ Valid conversation rate below threshold ({valid_rate:.1f}% < 70%)")
    if avg_quality < 6.0:
        alerts.append(f"⚠️ Average quality below threshold ({avg_quality:.1f} < 6.0)")
    if utilization >= 80:
        alerts.append(f"⚠️ Capacity usage high ({utilization:.1f}% ≥ 80%)")
    
    if alerts:
        print("\n🚨 ALERTS")
        for alert in alerts:
            print(f"   {alert}")
    else:
        print("\n✅ No alerts - All metrics within healthy ranges")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    if empty_convs > 0:
        print(f"   • Clean up {empty_convs} empty conversations")
    if avg_quality < 8.0:
        print("   • Review recent imports for quality improvements")
    if utilization < 50:
        print("   • Capture more strategic conversations (underutilized)")
    if valid_rate >= 90 and avg_quality >= 8.0:
        print("   • Excellent performance - maintain current practices")
    
    # Conversation captures check
    captures_dir = Path('cortex-brain/documents/conversation-captures')
    if captures_dir.exists():
        captures_count = len(list(captures_dir.glob('*.md')))
        print(f"\n📚 CONVERSATION CAPTURES: {captures_count} strategic documents")
        
        # Check capture targets
        if config_path.exists() and 'capture_targets' in config:
            targets = config['capture_targets']
            current = targets.get('current_count', 0)
            short_term = targets.get('short_term_goal', 0)
            
            if captures_count >= short_term:
                print(f"   ✅ Short-term goal achieved! ({captures_count}/{short_term})")
            else:
                remaining = short_term - captures_count
                print(f"   ⏳ Progress toward short-term goal: {captures_count}/{short_term} ({remaining} remaining)")
    
    conn.close()
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    check_tier1_utilization()
