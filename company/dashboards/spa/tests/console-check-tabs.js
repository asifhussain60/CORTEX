// Quick Console Test Script
// Paste this into browser console to check all tabs programmatically

(async function checkAllTabs() {
  console.log('🚀 Starting automated tab check...\n');
  
  const tabs = document.querySelectorAll('[role="tab"]');
  const results = [];
  
  for (let i = 0; i < tabs.length; i++) {
    const tab = tabs[i];
    const tabText = tab.textContent.trim();
    const panelId = tab.getAttribute('aria-controls');
    
    console.log(`${i + 1}. Checking: ${tabText}`);
    
    // Click tab
    tab.click();
    
    // Wait for deferred rendering
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Check panel visibility
    const panel = document.getElementById(panelId);
    const isHidden = panel?.getAttribute('aria-hidden') === 'true';
    const hasContent = panel?.children.length > 0;
    
    if (!isHidden && hasContent) {
      console.log(`   ✅ Loaded successfully (${panel.children.length} elements)`);
      results.push({ tab: tabText, status: '✅ Success' });
    } else if (!isHidden && !hasContent) {
      console.log(`   ⚠️ Visible but empty`);
      results.push({ tab: tabText, status: '⚠️ Empty' });
    } else {
      console.log(`   ❌ Panel hidden`);
      results.push({ tab: tabText, status: '❌ Error' });
    }
  }
  
  // Summary
  console.log('\n📊 Summary:');
  console.table(results);
  
  const successful = results.filter(r => r.status === '✅ Success').length;
  console.log(`\n✅ ${successful}/${results.length} tabs loaded successfully`);
  
  // Check deferred renderer
  if (window.cortexDashboard?.deferredRenderer) {
    const pending = window.cortexDashboard.deferredRenderer.getPendingCount();
    console.log(`⏳ Deferred renders pending: ${pending}`);
  }
  
  return results;
})();
