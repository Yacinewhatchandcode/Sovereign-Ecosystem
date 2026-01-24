import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright, expect

class SovereignAutomation:
    def __init__(self, base_url="http://localhost:8082"):
        self.base_url = base_url
        self.results = []
        self.screenshots_dir = "outputs/e2e_screenshots"
        import os
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def log_result(self, test_id, name, success, details=""):
        res = {
            "id": test_id,
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(res)
        status = "✅" if success else "❌"
        print(f"{status} [{test_id}] {name}")

    async def run_suite(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            # Enable logging
            page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))
            
            # --- PHASE 1: CORE PLATFORM ---
            try:
                await page.goto(self.base_url)
                await page.wait_for_selector(".header", timeout=10000)
                await expect(page).to_have_title(re.compile("AZIREM Sovereign"))
                self.log_result("CP-001", "Smoke Test - Page Load", True)
            except Exception as e:
                self.log_result("CP-001", "Smoke Test - Page Load", False, str(e))

            # Check Layout Panels (Corrected Selectors)
            panels = [
                (".header", "Header"),
                (".sidebar-left", "Left Sidebar"),
                (".center-content", "Main Content Area"),
                (".sidebar-right", "Right Sidebar"),
                (".terminal-panel", "Terminal Panel")
            ]
            for p_selector, p_name in panels:
                try:
                    await expect(page.locator(p_selector)).to_be_visible()
                    self.log_result("CP-LAYOUT", f"Panel Visibility: {p_name}", True)
                except Exception as e:
                    self.log_result("CP-LAYOUT", f"Panel Visibility: {p_name}", False, str(e))

            # --- PHASE 2: NAVIGATION & MODE SWITCHING ---
            modes = [
                ("AGENT VIEW", "#tab-agent", "video-player"),
                ("BYTEBOT DESKTOP", "#tab-bytebot", "bytebot-vnc"),
                ("3D NUCLEUS", "#tab-nucleus", "nucleus-3d")
            ]
            
            for tab_name, tab_id, target_id in modes:
                try:
                    # Switch tab using ID (first match)
                    await page.wait_for_selector(tab_id, timeout=10000)
                    await page.locator(tab_id).first.click()
                    await asyncio.sleep(1.2) # Wait for transition/init
                    
                    # Larger timeout for 3D Nucleus
                    timeout = 15000 if target_id == "nucleus-3d" else 5000
                    await expect(page.locator(f"#{target_id}")).to_be_visible(timeout=timeout)
                    self.log_result("CP-NAV", f"Switch to {tab_name}", True)
                except Exception as e:
                    self.log_result("CP-NAV", f"Switch to {tab_name}", False, str(e))

            # --- PHASE 3: QUICK ACTIONS (Actuation) ---
            # Handle prompt dialogs automatically
            page.on("dialog", lambda dialog: dialog.accept("E2E_TEST_INPUT"))

            actions = [
                ("Run Evolution", "Triggering REAL evolution cycle"),
                ("Mesh Audit", "Gathering technical intelligence"),
                ("API Workbench", "endpoint-item"), 
                ("Web Search", "Web Search triggered"),
                ("aSiReM Speak", "aSiReM: speaking"),
                ("Veo3 Credits", "videos left")
            ]

            for btn_text, log_anchor in actions:
                try:
                    # Target specific card using combined selector
                    card = page.locator(".agent-card").filter(has_text=btn_text).first
                    await card.click()
                    if log_anchor.startswith("endpoint"):
                        await page.wait_for_selector(f".{log_anchor}", timeout=5000)
                        await page.locator(".close-btn").click() 
                    else:
                        # Some logs are in Activity, some in Terminal
                        await asyncio.sleep(1)
                        content = await page.content()
                        if log_anchor.lower() in content.lower():
                            self.log_result("QA-ACTION", f"Trigger {btn_text}", True)
                        else:
                            self.log_result("QA-ACTION", f"Trigger {btn_text}", False, f"Expected '{log_anchor}' not found in UI")
                except Exception as e:
                    self.log_result("QA-ACTION", f"Trigger {btn_text}", False, str(e))
                finally:
                    # Cleanup modals after action
                    await page.evaluate('''() => {
                        if (typeof closeAgentViewer === 'function') closeAgentViewer();
                        if (typeof closeApiConsole === 'function') closeApiConsole();
                        if (typeof closePodcastPanel === 'function') closePodcastPanel();
                    }''')
                    await asyncio.sleep(0.3)

            # --- PHASE 4: AGENT FLEET (EXHAUSTIVE) ---
            agent_list = [
                "Scanner", "Classifier", "Extractor", "Summarizer", "Evolution", 
                "Researcher", "Architect", "Memory", "Embedding", "DocGen"
            ]
            for agent in agent_list:
                try:
                    # Target specific card to avoid ambiguity
                    card = page.locator(f".agent-card:has-text('{agent}')").first
                    await card.click()
                    await asyncio.sleep(0.3)
                    await expect(page.locator("#viewer-video")).to_be_visible()
                    self.log_result("AG-FLEET", f"Select {agent}", True)
                except Exception as e:
                    self.log_result("AG-FLEET", f"Select {agent}", False, str(e))
                finally:
                    # Close viewer so it doesn't block next agent click
                    await page.evaluate('if (typeof closeAgentViewer === "function") closeAgentViewer();')
                    await asyncio.sleep(0.2)

            # --- PHASE 5: BYTEBOT ACTUATION ---
            try:
                await page.click("text=BYTEBOT DESKTOP")
                # Wait for VNC content
                await page.wait_for_selector("#bytebot-vnc iframe", timeout=10000)
                self.log_result("BB-001", "ByteBot Desktop iframe Loaded", True)
                
                # Check Actuation Panel
                await expect(page.locator(".agent-action-panel")).to_be_visible()
                self.log_result("BB-002", "Actuation Control Visible", True)
            except Exception as e:
                self.log_result("BB-001", "ByteBot Check Failed", False, str(e))

            # --- PHASE 6: REPORTING & DATA RETRIEVAL ---
            report_path = "outputs/e2e_automation_report.json"
            summary_path = "outputs/e2e_summary.md"
            
            with open(report_path, "w") as f:
                json.dump(self.results, f, indent=4)
            
            # Generate MD Summary
            total = len(self.results)
            passed = sum(1 for r in self.results if r["success"])
            failed = total - passed
            
            md = f"# 📊 Sovereign E2E Automation Summary\n\n"
            md += f"- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            md += f"- **Total Tests**: {total}\n"
            md += f"- **Passed**: ✅ {passed}\n"
            md += f"- **Failed**: ❌ {failed}\n\n"
            md += "| ID | Test Name | Result | Details |\n|---|---|---|---|\n"
            for r in self.results:
                md += f"| {r['id']} | {r['name']} | {'✅' if r['success'] else '❌'} | {r['details']} |\n"
            
            with open(summary_path, "w") as f:
                f.write(md)

            print(f"\n🚀 Comprehensive E2E Finished. Pass: {passed}/{total}")
            await browser.close()

if __name__ == "__main__":
    import re
    automation = SovereignAutomation()
    asyncio.run(automation.run_suite())
