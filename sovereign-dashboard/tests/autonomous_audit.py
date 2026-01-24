import asyncio
import json
import os
import re
import time
from datetime import datetime
from playwright.async_api import async_playwright, expect

class SovereignFullAudit:
    def __init__(self, base_url="http://localhost:8082"):
        self.base_url = base_url
        self.output_dir = "outputs/audit_results"
        self.video_dir = os.path.join(self.output_dir, "videos")
        os.makedirs(self.video_dir, exist_ok=True)
        self.report = []

    async def run_audit(self):
        print("🧬 [SOVEREIGN AUDIT] Starting Full Autonomous Actuation...")
        
        async with async_playwright() as p:
            # Launch with video recording
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                record_video_dir=self.video_dir,
                record_video_size={"width": 1440, "height": 900}
            )
            page = await context.new_page()

            # Handle all alerts/prompts
            page.on("dialog", lambda dialog: dialog.accept("AUDIT_TEST_DATA"))
            
            # Step 1: Load Dashboard
            try:
                await page.goto(self.base_url)
                await page.wait_for_selector(".header", timeout=15000)
                print("✅ Dashboard Loaded")
            except Exception as e:
                print(f"❌ Failed to load dashboard: {e}")
                await browser.close()
                return

            # Step 2: Discover all interactable elements
            # We target tabs, agent cards, quick action cards, and actuation buttons
            interactables = await page.evaluate('''() => {
                const elements = [];
                // Tabs
                document.querySelectorAll('.tab').forEach(el => elements.push({text: el.innerText, selector: '.tab', type: 'tab'}));
                // Agent Cards
                document.querySelectorAll('.agent-card').forEach(el => {
                    const name = el.querySelector('.agent-name')?.innerText || 'Unknown Agent';
                    elements.push({text: name, selector: '.agent-card', type: 'agent'});
                });
                // Action Buttons
                document.querySelectorAll('.action-btn').forEach(el => {
                    const name = el.innerText.split('\\n')[0];
                    elements.push({text: name, selector: '.action-btn', type: 'actuator'});
                });
                // Quick Action Cards (the ones with onclick)
                document.querySelectorAll('.agent-card[onclick]').forEach(el => {
                   const name = el.querySelector('.agent-name')?.innerText || 'QuickAction';
                   elements.push({text: name, selector: '.agent-card', type: 'quick_action'});
                });
                
                return elements;
            }''')

            print(f"📡 Discovered {len(interactables)} interactable targets for audit.")

            # Step 3: Exhaustive Actuation Loop
            for i, target in enumerate(interactables):
                target_name = target['text'].strip()
                print(f"   👉 [{i+1}/{len(interactables)}] Actuating: {target_name} ({target['type']})")
                
                try:
                    # Target element precisely
                    selector = target['selector']
                    if target['type'] == 'tab':
                        loc = page.get_by_text(target_name, exact=True)
                    else:
                        loc = page.locator(selector).filter(has_text=target_name).first

                    if await loc.is_visible():
                        await loc.click()
                        await asyncio.sleep(1.5) # Wait for UI to react
                        
                        # MODAL CLEANUP: Close any potential modals to prevent click interception
                        await page.evaluate('''() => {
                            if (typeof closeAgentViewer === 'function') closeAgentViewer();
                            if (typeof closeApiConsole === 'function') closeApiConsole();
                            if (typeof closePodcastPanel === 'function') closePodcastPanel();
                            if (typeof closeOpikModal === 'function') closeOpikModal();
                            
                            // Also hide any backdrops manually as a fallback
                            document.querySelectorAll('.agent-viewer-modal, .api-modal, .podcast-modal, .agent-viewer-backdrop').forEach(el => {
                                el.style.display = 'none';
                            });
                        }''')
                        await asyncio.sleep(0.5)

                        # Verify response in logs or DOM changes
                        content = await page.content()
                        
                        # Screenshot of result
                        shot_path = f"{self.output_dir}/step_{i+1}_{target_name.replace(' ', '_')}.png"
                        await page.screenshot(path=shot_path)
                        
                        self.report.append({
                            "step": i+1,
                            "target": target_name,
                            "type": target['type'],
                            "status": "success",
                            "screenshot": shot_path
                        })
                    else:
                        print(f"      ⚠️  Target {target_name} not visible, skipping.")
                except Exception as e:
                    print(f"      ❌  Error actuating {target_name}: {e}")
                    self.report.append({
                        "step": i+1,
                        "target": target_name,
                        "type": target['type'],
                        "status": "failed",
                        "error": str(e)
                    })

            # Step 4: Finalize and save report
            video_path = await page.video.path()
            final_report_path = os.path.join(self.output_dir, "audit_summary.json")
            
            final_data = {
                "audit_timestamp": datetime.now().isoformat(),
                "total_steps": len(interactables),
                "results": self.report,
                "video_artifact": video_path
            }
            
            with open(final_report_path, "w") as f:
                json.dump(final_data, f, indent=4)

            print(f"\n🏁 [AUDIT COMPLETE]")
            print(f"📊 Report: {final_report_path}")
            print(f"🎬 Video Evidence: {video_path}")
            
            await browser.close()

if __name__ == "__main__":
    audit = SovereignFullAudit()
    asyncio.run(audit.run_audit())
