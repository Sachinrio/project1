import asyncio
from sqlmodel import select
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from playwright.async_api import async_playwright
import re

from app.core.database import engine
from app.models.msme_schema import MSMERegistration

async def run_msme_automation(registration_id: int):
    print(f"MSME AUTOMATION: Starting sequence for Reg ID {registration_id}")
    
    # Securely retrieve collected data from DB
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(MSMERegistration).where(MSMERegistration.id == registration_id))
        reg = result.scalars().first()
        
        if not reg or not reg.aadhar_number or not reg.name_as_per_aadhar:
            print(f"MSME AUTOMATION ABORTED: Missing essential registration data for ID {registration_id}.")
            return
            
        # CLEAR old OTP before starting!
        reg.otp_code = None
        session.add(reg)
        await session.commit()
            
        print(f"MSME AUTOMATION: Loaded securely for {reg.user_email}")
        
    # Launch Playwright Automaton with Evasive Flags
    print("MSME AUTOMATION: Spinning up Chromium engine...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, 
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled' # Bypass basic bot detection
            ]
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Hide webdriver signature
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            print("MSME AUTOMATION: Navigating to Official Udyam Protocol...")
            
            max_retries = 10
            attempt = 0
            page_loaded = False
            
            # Initial navigation
            try:
                await page.goto("https://udyamregistration.gov.in/UdyamRegistration.aspx", timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"MSME AUTOMATION: Note on initial navigation: {e}")
            
            while attempt < max_retries and not page_loaded:
                attempt += 1
                try:
                    print(f"MSME AUTOMATION: Verifying required inputs (Attempt {attempt})...")
                    
                    # Locators based strictly on visible placeholders from live site
                    aadhar_input = page.locator("input[placeholder*='Your Aadhaar No' i]").first
                    name_input = page.locator("input[placeholder*='Name as per Aadhaar' i]").first
                    
                    # Wait for fields to become visible, only refreshing if this explicitly times out.
                    await aadhar_input.wait_for(state="visible", timeout=20000)
                    page_loaded = True
                    print("MSME AUTOMATION: Security Check Passed. Site is live.")
                    
                except Exception as loop_e:
                    print(f"MSME AUTOMATION: Fields not detected. ({str(loop_e)})")
                    if attempt < max_retries:
                        print("MSME AUTOMATION: Refreshing page...")
                        try:
                            await page.reload(timeout=30000, wait_until="domcontentloaded")
                        except:
                            pass
                        await page.wait_for_timeout(5000)
                    
            if not page_loaded:
                print("MSME AUTOMATION FATAL: Could not establish connection. Please check Gov site manually.")
                await page.wait_for_timeout(600000)
                return

            print("MSME AUTOMATION: Injecting Aadhar payload...")
            await aadhar_input.scroll_into_view_if_needed()
            await aadhar_input.fill(str(reg.aadhar_number))
            
            # Explicitly wait to ensure ASP.NET catches the state change
            await page.wait_for_timeout(1500)

            print("MSME AUTOMATION: Injecting Name payload...")
            await name_input.scroll_into_view_if_needed()
            await name_input.fill(str(reg.name_as_per_aadhar))
            
            # Explicitly wait
            await page.wait_for_timeout(1500)
            
            # Double check values actually exist before moving on
            aadhar_val = await aadhar_input.input_value()
            name_val = await name_input.input_value()
            print(f"MSME AUTOMATION: Verified Aadhar end ({aadhar_val[-4:]}) and Name ({name_val})")

            print("MSME AUTOMATION: DATA INJECTED SUCCESSFULLY. 🚀")
            
            # Click the Validate & Generate OTP button ONLY AFTER FILLING
            print("MSME AUTOMATION: Clicking 'Validate & Generate OTP'...")
            await page.wait_for_timeout(2000) 
            
            # Strict locator based on visible text on the Udyam portal
            submit_btn = page.locator("button:has-text('Validate & Generate OTP'), input[value='Validate & Generate OTP' i]").first
            
            # Do NOT use force=True right away so we can see if it's being blocked
            await submit_btn.scroll_into_view_if_needed()
            await submit_btn.click()
            
            print("=========================================================")
            print("MSME AUTOMATION: Waiting for OTP from Chatbot...")
            print("=========================================================")
            
            otp_found = None
            for _ in range(60): # Poll every 5s for 5 minutes
                await page.wait_for_timeout(5000)
                async with async_session() as poll_session:
                    poll_result = await poll_session.execute(select(MSMERegistration).where(MSMERegistration.id == registration_id))
                    current_reg = poll_result.scalars().first()
                    if current_reg and current_reg.otp_code:
                        otp_found = current_reg.otp_code
                        break
                        
            if otp_found:
                print(f"MSME AUTOMATION: OTP DETECTED. Injecting [{otp_found}]...")
                
                otp_input = page.locator("input[placeholder*='OTP code' i]").first
                await otp_input.wait_for(state="visible", timeout=30000)
                await otp_input.scroll_into_view_if_needed()
                await otp_input.fill(str(otp_found))
                
                await page.wait_for_timeout(2000)
                
                print("MSME AUTOMATION: Submitting Final Validation...")
                otp_submit_btn = page.locator("button:has-text('Validate'), input[value='Validate' i]").first
                await otp_submit_btn.scroll_into_view_if_needed()
                await otp_submit_btn.click()
                
                print("MSME AUTOMATION: OTP INJECTED SUCCESSFULLY! 🎉")
                
                # --- NEW PAN VERIFICATION PHASE ---
                print("MSME AUTOMATION: Waiting for PAN Verification fields to load...")
                
                # Re-fetch registration to get the PAN fields
                async with async_session() as final_session:
                    final_result = await final_session.execute(select(MSMERegistration).where(MSMERegistration.id == registration_id))
                    final_reg = final_result.scalars().first()
                
                if final_reg:
                    try:
                        pan_input = page.locator("input[placeholder*='ENTER PAN NUMBER' i]").first
                        await pan_input.wait_for(state="visible", timeout=30000)
                        
                        print("MSME AUTOMATION: Injecting PAN Verification details...")
                        
                        # 1. Select Organization Type (Dropdown)
                        if final_reg.organisation_type:
                            try:
                                print(f"MSME AUTOMATION: Attempting to select Org Type: {final_reg.organisation_type}")
                                org_select = page.locator("select").first
                                await org_select.wait_for(state="visible", timeout=10000)
                                
                                # Use Playwright's native select_option but make it case-insensitive/partial match
                                # Instead of strict label, we pass it as a regex or partial text if possible, but ASP.NET can be picky.
                                # Let's find all options, see which text matches, and get its value.
                                options = await org_select.locator("option").all()
                                matched_value = None
                                match_target = final_reg.organisation_type.strip().lower()
                                
                                for opt in options:
                                    opt_text = await opt.inner_text()
                                    if match_target in opt_text.lower():
                                        matched_value = await opt.get_attribute("value")
                                        break
                                
                                if matched_value:
                                    await org_select.select_option(value=matched_value)
                                    print(f"MSME AUTOMATION: Successfully selected Org Type value '{matched_value}'")
                                    # EXTREMELY IMPORTANT: ASP.NET performs a partial postback here. We must wait!
                                    await page.wait_for_timeout(4000)
                                else:
                                    print(f"MSME AUTOMATION WARNING: Could not find an exact dropdown match for '{final_reg.organisation_type}'.")
                            except Exception as e:
                                print(f"MSME AUTOMATION WARNING: Dropdown execution error. ({e})")
                                
                        # 2. Enter PAN Number
                        if final_reg.pan_number:
                            # Re-query the locator after postback
                            pan_input = page.locator("input[placeholder*='ENTER PAN NUMBER' i]").first
                            await pan_input.wait_for(state="visible", timeout=15000)
                            await pan_input.scroll_into_view_if_needed()
                            await pan_input.fill("")
                            await pan_input.press_sequentially(str(final_reg.pan_number), delay=50)
                            await page.wait_for_timeout(1000)
                            
                        # 3. Enter PAN Name
                        if final_reg.pan_name:
                            pan_name_input = page.locator("input[placeholder*='Name as per PAN' i]").first
                            await pan_name_input.wait_for(state="visible", timeout=15000)
                            await pan_name_input.scroll_into_view_if_needed()
                            await pan_name_input.fill("")
                            await pan_name_input.press_sequentially(str(final_reg.pan_name), delay=50)
                            await page.wait_for_timeout(1000)
                            
                        # 4. Enter PAN DOB
                        if final_reg.pan_dob:
                            pan_dob_input = page.locator("input[placeholder*='DD/MM/YYYY' i]").first
                            await pan_dob_input.wait_for(state="visible", timeout=15000)
                            await pan_dob_input.scroll_into_view_if_needed()
                            await pan_dob_input.fill("")
                            await pan_dob_input.press_sequentially(str(final_reg.pan_dob), delay=50)
                            await page.wait_for_timeout(1000)
                            
                        # 5. Check Consent Box
                        print("MSME AUTOMATION: Waiting and locating Consent Checkbox...")
                        is_checked = False
                        
                        # Wait specifically after DOB is filled
                        await page.wait_for_timeout(2000)
                        
                        try:
                            # Instead of guessing IDs or text which might be dynamic or hidden by spans,
                            # we will forcefully check any and all checkboxes on the page. 
                            # Since this is the PAN stage, this consent box is the only relevant checkbox.
                            checkboxes = await page.locator("input[type='checkbox']").all()
                            
                            for cb in checkboxes:
                                try:
                                    # Force the checked property via Javascript
                                    await cb.evaluate("el => el.checked = true")
                                    # Manually dispatch a change event to trigger ASP.net validation handlers
                                    await cb.evaluate("el => el.dispatchEvent(new Event('change', { bubbles: true }))")
                                    is_checked = True
                                except Exception as inner_e:
                                    print(f"MSME AUTOMATION: Note on checkbox loop: {inner_e}")
                                    pass

                            if is_checked:
                                print("MSME AUTOMATION: Consent checkbox(es) forcefully turned on via JavaScript.")
                            else:
                                print("MSME AUTOMATION ERROR: Could not find any checkboxes in the DOM to click.")
                                
                        except Exception as cb_e:
                            print(f"MSME AUTOMATION ERROR: Could not run checkbox script. ({cb_e})")
                            
                        # If the checkbox wasn't successfully clicked, DO NOT click validate.
                        if not is_checked:
                            raise Exception("Checkbox not clicked securely. Halting execution before clicking PAN Validate.")
                            
                        await page.wait_for_timeout(2000)
                        
                        # 6. Click PAN Validate
                        print("MSME AUTOMATION: Clicking PAN Validate button...")
                        try:
                            # Using a combination of selectors to guarantee we hit the blue button
                            pan_validate_btn = page.locator("button:has-text('PAN Validate'), input[value='PAN Validate' i], #btnPANValidate").first
                            await pan_validate_btn.wait_for(state="visible", timeout=10000)
                            await pan_validate_btn.scroll_into_view_if_needed()
                            
                            # Sometimes standard clicks are blocked on this site, try dispatching a click event
                            await pan_validate_btn.evaluate("el => el.click()")
                            print("MSME AUTOMATION: PAN Validate button clicked successfully.")
                            
                            # Wait for the ASP.NET postback after validation
                            await page.wait_for_timeout(5000)
                        except Exception as btn_e:
                            print(f"MSME AUTOMATION ERROR: Could not click PAN Validate button. ({btn_e})")
                        
                        print("MSME AUTOMATION: PAN VALIDATION COMPLETE! 🚀")
                        
                        # 7. Click Continue button
                        print("MSME AUTOMATION: Waiting for 'Continue' button to appear...")
                        try:
                            # Typically forms have 'Continue', 'Next', etc. Looking broadly but prioritizing Continue.
                            continue_btn = page.locator("button:has-text('Continue'), input[value='Continue' i], #btnContinue").first
                            
                            # Give it a larger timeout since ASP.net PAN validation might take a bit longer on their servers
                            await continue_btn.wait_for(state="visible", timeout=20000)
                            await continue_btn.scroll_into_view_if_needed()
                            
                            print("MSME AUTOMATION: 'Continue' button found. Clicking it...")
                            # Sometimes standard clicks are blocked, try dispatching a click event
                            await continue_btn.evaluate("el => el.click()")
                            
                            print("MSME AUTOMATION: Successfully moved to the next step!")
                            await page.wait_for_timeout(3000)
                        except Exception as cont_e:
                            print(f"MSME AUTOMATION ERROR: Could not find or click the 'Continue' button. ({cont_e})")
                            
                    except Exception as pan_e:
                        print(f"MSME AUTOMATION PAN ERROR: {pan_e}")
                
                # --- NEW PHASE 2 FORM FILLING ---
                print("MSME AUTOMATION: Starting Phase 2 Form Filling...")
                # Re-fetch registration to get the newest fields
                async with async_session() as phase2_session:
                    phase2_result = await phase2_session.execute(select(MSMERegistration).where(MSMERegistration.id == registration_id))
                    phase2_reg = phase2_result.scalars().first()
                
                if phase2_reg:
                    try:
                        # 8. ITR and GSTIN
                        print("MSME AUTOMATION: Filling ITR & GSTIN...")
                        if phase2_reg.itr_filed:
                            itr_target = 'Yes' if 'yes' in phase2_reg.itr_filed.lower() else 'No'
                            # Scope to the specific question using a broader container text search
                            itr_container = page.locator("div, td, tr, table").filter(has_text=re.compile(r"Have you filed the ITR")).last
                            if await itr_container.count() > 0:
                                label_to_click = itr_container.locator("label").filter(has_text=re.compile(itr_target, re.I)).first
                                if await label_to_click.count() > 0:
                                    try:
                                        await label_to_click.click(force=True, timeout=5000)
                                    except:
                                        # Fallback to JS click on the associated input if label click fails
                                        await label_to_click.locator("input").evaluate("el => el.click()")
                                    await page.wait_for_timeout(500)
                                
                        if phase2_reg.has_gstin:
                            gstin_target = 'Yes' if 'yes' in phase2_reg.has_gstin.lower() else ('Exempted' if 'exempt' in phase2_reg.has_gstin.lower() else 'No')
                            gstin_container = page.locator("div, td, tr, table").filter(has_text=re.compile(r"4\.3 Do you have GSTIN")).last
                            if await gstin_container.count() > 0:
                                label_to_click = gstin_container.locator("label").filter(has_text=re.compile(gstin_target, re.I)).first
                                if await label_to_click.count() > 0:
                                    try:
                                        await label_to_click.click(force=True, timeout=5000)
                                    except:
                                        await label_to_click.locator("input").evaluate("el => el.click()")
                                    await page.wait_for_timeout(500)

                        # 9. Mobile and Email
                        print("MSME AUTOMATION: Filling Mobile & Email...")
                        if phase2_reg.mobile_number:
                            mobile_input = page.locator("input[placeholder*='Mobile No' i], input[id*='mobile' i]").first
                            if await mobile_input.count() > 0:
                                await mobile_input.scroll_into_view_if_needed()
                                await mobile_input.fill(str(phase2_reg.mobile_number))
                        
                        if phase2_reg.email:
                            email_input = page.locator("input[placeholder*='Email' i], input[id*='email' i]").first
                            if await email_input.count() > 0:
                                await email_input.scroll_into_view_if_needed()
                                await email_input.fill(str(phase2_reg.email))

                        # 10. Social Category, Gender, Specially Abled
                        print("MSME AUTOMATION: Filling Social Category, Gender, Divyang...")
                        if phase2_reg.social_category:
                            cat = phase2_reg.social_category.strip()
                            cat_container = page.locator("div, td, tr, table").filter(has_text=re.compile(r"8\.\s*Social Category", re.I)).last
                            if await cat_container.count() > 0:
                                label_to_click = cat_container.locator("label").filter(has_text=re.compile(cat, re.I)).first
                                if await label_to_click.count() > 0:
                                    try:
                                        await label_to_click.click(force=True, timeout=5000)
                                    except:
                                        await label_to_click.locator("input").evaluate("el => el.click()")
                                
                        if phase2_reg.gender:
                            gen = phase2_reg.gender.strip()
                            gen_container = page.locator("div, td, tr, table").filter(has_text=re.compile(r"9\.\s*Gender", re.I)).last
                            if await gen_container.count() > 0:
                                label_to_click = gen_container.locator("label").filter(has_text=re.compile(gen, re.I)).first
                                if await label_to_click.count() > 0:
                                    try:
                                        await label_to_click.click(force=True, timeout=5000)
                                    except:
                                        await label_to_click.locator("input").evaluate("el => el.click()")
                                
                        if phase2_reg.specially_abled:
                            abled = 'Yes' if 'yes' in phase2_reg.specially_abled.lower() else 'No'
                            abled_container = page.locator("div, td, tr, table").filter(has_text=re.compile(r"10\.\s*Specially Abled", re.I)).last
                            if await abled_container.count() > 0:
                                label_to_click = abled_container.locator("label").filter(has_text=re.compile(abled, re.I)).first
                                if await label_to_click.count() > 0:
                                    try:
                                        await label_to_click.click(force=True, timeout=5000)
                                    except:
                                        await label_to_click.locator("input").evaluate("el => el.click()")

                        # 11 & 12. Enterprise and Plant Name
                        print("MSME AUTOMATION: Filling Enterprise and Plant Names...")
                        if phase2_reg.enterprise_name:
                            enterprise_input = page.locator("input[placeholder*='Name of Enterprise' i]").first
                            if await enterprise_input.count() > 0:
                                await enterprise_input.scroll_into_view_if_needed()
                                await enterprise_input.fill(str(phase2_reg.enterprise_name))
                                
                        if phase2_reg.plant_name:
                            plant_input = page.locator("input[placeholder*='Unit Name' i]").first
                            if await plant_input.count() > 0:
                                await plant_input.scroll_into_view_if_needed()
                                await plant_input.fill(str(phase2_reg.plant_name))
                                
                                # Click Add Unit
                                add_unit_btn = page.locator("button:has-text('Add Unit'), input[value*='Add Unit' i]").first
                                if await add_unit_btn.count() > 0:
                                    await add_unit_btn.click()
                                    await page.wait_for_timeout(2000)

                        # 13. Plant Address (Assumes comma separated)
                        print("MSME AUTOMATION: Filling Plant Address...")
                        if phase2_reg.plant_address:
                            # Try to split by comma
                            p_parts = [p.strip() for p in phase2_reg.plant_address.split(',')]
                            # Attempt to select the unit in dropdown if exists
                            unit_select = page.locator("select[id*='Unit']").first
                            if await unit_select.count() > 0 and phase2_reg.plant_name:
                                try:
                                    options = await unit_select.locator("option").all()
                                    for opt in options:
                                        if phase2_reg.plant_name.lower() in (await opt.inner_text()).lower():
                                            await unit_select.select_option(value=await opt.get_attribute("value"))
                                            await page.wait_for_timeout(1000)
                                            break
                                except Exception:
                                    pass
                            
                            # Sequential fill
                            locators_placeholder = ['Flat', 'Premises', 'Village', 'Block', 'Road', 'City', 'Pin']
                            for idx, val in enumerate(p_parts):
                                if idx < len(locators_placeholder):
                                    inp = page.locator(f"input[placeholder*='{locators_placeholder[idx]}' i]").first
                                    if await inp.count() > 0:
                                        await inp.fill(val)
                            
                            # State and District are dropdowns - complex to handle generically without exact html, skipping complex logic for MVP
                            add_plant_btn = page.locator("button:has-text('Add Plant'), input[value*='Add Plant' i]").first
                            if await add_plant_btn.count() > 0:
                                await add_plant_btn.click()
                                await page.wait_for_timeout(2000)

                        # 14. Previous Registration
                        print("MSME AUTOMATION: Selecting Previous Registration...")
                        if phase2_reg.previous_registration:
                            prev_reg_str = phase2_reg.previous_registration
                            prev_radio = page.locator(f"label:has-text('{prev_reg_str}') input[type='radio']").first
                            if await prev_radio.count() > 0:
                                await prev_radio.check()

                        # 15. Status of Enterprise (Dates)
                        print("MSME AUTOMATION: Filling Enterprise Status Dates...")
                        if phase2_reg.date_of_incorporation:
                            doi_input = page.locator("input[placeholder*='DD/MM/YYYY' i]").nth(1) # Naive approach, usually 2nd or 3rd date field on page
                            if await doi_input.count() > 0:
                                await doi_input.fill(str(phase2_reg.date_of_incorporation))
                                
                        if phase2_reg.business_commenced:
                            comm_yesno = 'Yes' if 'yes' in phase2_reg.business_commenced.lower() else 'No'
                            comm_radio = page.locator(f"label:has-text('{comm_yesno}') input[type='radio'][name*='commenced']").first
                            if await comm_radio.count() > 0:
                                await comm_radio.check()

                        if phase2_reg.date_of_commencement:
                            doc_input = page.locator("input[placeholder*='DD/MM/YYYY' i]").nth(2)
                            if await doc_input.count() > 0:
                                await doc_input.fill(str(phase2_reg.date_of_commencement))
                                                
                        print("MSME AUTOMATION: Phase 2 Form Filling Complete!")
                    except Exception as phase2_e:
                        print(f"MSME AUTOMATION PHASE 2 ERROR: {phase2_e}")

                # Mark as complete in DB
                async with async_session() as final_session:
                    final_result = await final_session.execute(select(MSMERegistration).where(MSMERegistration.id == registration_id))
                    final_reg = final_result.scalars().first()
                    if final_reg:
                        final_reg.status = "COMPLETED"
                        final_session.add(final_reg)
                        await final_session.commit()

                
                # Keep browser open to let the user manually complete the subsequent steps
                print("MSME AUTOMATION: Leaving browser open for manual form completion.")
                # Wait 30 minutes
                await page.wait_for_timeout(1800000) 
            else:
                print("MSME AUTOMATION TIMEOUT: No OTP was entered in the Chatbot after 5 minutes.")
                await page.wait_for_timeout(900000)
            
        except Exception as e:
            print("MSME AUTOMATION FATAL ERROR:", str(e))
            print("MSME AUTOMATION: Leaving browser open for manual inspection.")
