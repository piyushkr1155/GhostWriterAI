"""GhostWriter - Offline AI Horror Story Generator.

Every shadow has a story. Every story has a ghost.
Hacktoberfest Open-Source AI Challenge: "Ghost in the Machine"
"""
import time
import streamlit as st

from src.config import config
from src.ollama_client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    ModelNotFoundError,
    OllamaTimeoutError
)
from src.story_generator import StoryGenerator, StoryValidationError
from src.storage import GhostStorage, StoryRecord

# Page configuration
st.set_page_config(
    page_title="GhostWriter 👻 | Offline AI Horror Story Generator",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Atmospheric Horror Theme & Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');

/* Base Spooky Colors */
:root {
    --bg-dark: #09080e;
    --card-bg: #13101c;
    --card-border: #2d2442;
    --accent-orange: #ff6b35;
    --accent-purple: #7952b3;
    --blood-red: #d90429;
    --text-primary: #f0ecf7;
    --text-secondary: #a39cb2;
    --ghost-glow: rgba(255, 107, 53, 0.25);
}

/* Background Atmosphere */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1c142b 0%, #0c0a13 55%, #050408 100%);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Custom Horror Headers */
.spooky-header {
    font-family: 'Cinzel Decorative', Georgia, serif;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #ffffff 0%, #ff6b35 50%, #9d4edd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 35px var(--ghost-glow);
    margin-bottom: 0px;
    line-height: 1.15;
}

.spooky-tagline {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 1.25rem;
    color: #b5a9cb;
    margin-top: 6px;
    margin-bottom: 24px;
    letter-spacing: 0.5px;
}

/* Story Result Card */
.story-card {
    background: linear-gradient(180deg, #161222 0%, #0f0c18 100%);
    border: 1px solid #36284f;
    border-radius: 12px;
    padding: 32px 36px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(121, 82, 179, 0.15);
    margin: 20px 0;
    position: relative;
    overflow: hidden;
}

.story-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ff6b35, #7952b3, #d90429);
}

.story-title {
    font-family: 'Cinzel Decorative', Georgia, serif;
    font-size: 1.9rem;
    color: #ffedd8;
    margin-bottom: 12px;
    letter-spacing: 1px;
    text-shadow: 0 0 15px rgba(255, 107, 53, 0.3);
}

.story-meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid #281d3d;
}

.story-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.badge-orange { background: rgba(255, 107, 53, 0.15); color: #ff8c5a; border: 1px solid rgba(255, 107, 53, 0.3); }
.badge-purple { background: rgba(121, 82, 179, 0.2); color: #c499f3; border: 1px solid rgba(121, 82, 179, 0.35); }
.badge-red { background: rgba(217, 4, 41, 0.15); color: #ff4d6d; border: 1px solid rgba(217, 4, 41, 0.3); }
.badge-gray { background: rgba(255, 255, 255, 0.05); color: #a49db2; border: 1px solid rgba(255, 255, 255, 0.1); }

.story-body {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.15rem;
    line-height: 1.85;
    color: #e5dfed;
    white-space: pre-wrap;
    letter-spacing: 0.2px;
}

/* Sidebar Styles */
[data-testid="stSidebar"] {
    background-color: #0b0912;
    border-right: 1px solid #231b33;
}

/* Floating Fog Animation */
@keyframes fogDrift {
    0% { transform: translateX(-5%); opacity: 0.2; }
    50% { transform: translateX(5%); opacity: 0.35; }
    100% { transform: translateX(-5%); opacity: 0.2; }
}

.fog-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(ellipse at 80% 20%, rgba(121, 82, 179, 0.08) 0%, transparent 60%);
    animation: fogDrift 18s ease-in-out infinite;
}

/* Button & Widget Overrides */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #d90429 0%, #ff6b35 100%);
    color: #ffffff;
    font-weight: 700;
    font-size: 1.05rem;
    padding: 0.65rem 1.8rem;
    border-radius: 8px;
    border: none;
    box-shadow: 0 4px 18px rgba(255, 107, 53, 0.35);
    transition: all 0.25s ease;
}

div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(255, 107, 53, 0.55);
    background: linear-gradient(135deg, #e61c3d 0%, #ff7d4d 100%);
}

.status-box {
    padding: 14px 18px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 0.88rem;
}

.status-online {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
}

.status-offline {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #f87171;
}

.status-warning {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #fbbf24;
}
</style>
<div class="fog-overlay"></div>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize singletons in session state
if "storage" not in st.session_state:
    st.session_state.storage = GhostStorage()

if "client" not in st.session_state:
    st.session_state.client = OllamaClient()

if "generator" not in st.session_state:
    st.session_state.generator = StoryGenerator(client=st.session_state.client)

if "current_story" not in st.session_state:
    st.session_state.current_story = None

if "story_saved_flag" not in st.session_state:
    st.session_state.story_saved_flag = False

# Sidebar: Local AI Status & Diagnostics
with st.sidebar:
    st.markdown("### 👻 GhostWriter AI Status")
    
    # Check Ollama Health
    health = st.session_state.client.check_health()
    installed_models = health.get("models", [])
    
    # Model selection (dynamic dropdown from installed models, with fallback)
    available_choices = installed_models if installed_models else [config.default_model]
    if config.default_model not in available_choices:
        available_choices.insert(0, config.default_model)
        
    selected_model = st.selectbox(
        "Active Local Model",
        options=available_choices,
        index=0,
        help="Select which local open-weight model runs your horror inference."
    )
    
    # Update active model in client
    st.session_state.client.default_model = selected_model
    
    # Re-check status against the selected model
    model_is_ready = selected_model in installed_models or any(selected_model in m for m in installed_models)
    
    if health["is_running"] and model_is_ready:
        st.markdown(f"""
        <div class="status-box status-online">
            <strong>🟢 Ollama Online</strong> ({health['latency_ms']}ms)<br>
            <span style="font-size:0.8rem; color:#86efac;">
                Model <code>{selected_model}</code> is loaded & ready offline.
            </span>
        </div>
        """, unsafe_allow_html=True)
    elif health["is_running"] and not model_is_ready:
        st.markdown(f"""
        <div class="status-box status-warning">
            <strong>🟡 Ollama Online, Model Missing</strong><br>
            <span style="font-size:0.8rem;">
                Model <code>{selected_model}</code> is not pulled yet.
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.code(f"ollama pull {selected_model}", language="powershell")
    else:
        st.markdown(f"""
        <div class="status-box status-offline">
            <strong>🔴 Ollama Offline</strong><br>
            <span style="font-size:0.8rem;">
                Could not connect to {config.ollama_base_url}
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 To start Ollama on Windows, run:\n```powershell\nollama serve\n```")

    st.markdown("---")
    
    # Privacy & Offline Guarantee
    st.markdown("""
    **🔒 100% Offline & Private**  
    No cloud APIs. No user telemetry. All stories are conceived and saved directly on your device.
    """)
    
    # Grimoire Quick Stats
    stats = st.session_state.storage.get_stats()
    st.markdown(f"""
    **📜 The Haunted Grimoire**  
    - **{stats['total_stories']}** Stories Inscribed  
    - **{stats['favorite_stories']}** Bookmarked  
    - **{stats['total_words_written']:,}** Words of Dread
    """)

    st.markdown("---")
    st.caption("GhostWriter v1.0 • Hacktoberfest 2026")


# Main Application Header
col_hdr_icon, col_hdr_text = st.columns([0.08, 0.92])
with col_hdr_icon:
    st.markdown("<div style='font-size:3.5rem; line-height:1; margin-top:6px;'>👻</div>", unsafe_allow_html=True)
with col_hdr_text:
    st.markdown("<h1 class='spooky-header'>GHOSTWRITER</h1>", unsafe_allow_html=True)
    st.markdown("<p class='spooky-tagline'>Every shadow has a story. Every story has a ghost.</p>", unsafe_allow_html=True)


# Navigation Tabs
tab_summon, tab_archive, tab_manifesto = st.tabs([
    "🕯️ Summon a Nightmare",
    "📜 The Haunted Grimoire",
    "🔮 Open AI & Privacy"
])


# =========================================================================
# TAB 1: STORY GENERATOR
# =========================================================================
with tab_summon:
    st.markdown("##### Weave your horror story from the darkness within:")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        # Setting selection
        selected_setting = st.selectbox(
            "🏚️ Cursed Setting",
            options=config.settings,
            index=0,
            help="Where does the nightmare take place?"
        )
        custom_setting_input = ""
        if selected_setting == "Custom Setting...":
            custom_setting_input = st.text_input(
                "Specify your setting",
                placeholder="e.g., An abandoned Soviet submarine trapped in Arctic ice",
                max_chars=100
            )

        # Character selection
        selected_character = st.selectbox(
            "👤 The Unfortunate Protagonist",
            options=config.characters,
            index=0,
            help="Whose eyes witness the horror?"
        )
        custom_char_input = ""
        if selected_character == "Custom Character...":
            custom_char_input = st.text_input(
                "Specify your character",
                placeholder="e.g., A sleep-deprived air traffic controller",
                max_chars=100
            )

    with col_input2:
        # Horror Style
        selected_style = st.selectbox(
            "🩸 Horror Subgenre / Style",
            options=list(config.styles.keys()),
            index=1,
            help="The psychological atmosphere and terror pacing."
        )
        # Display short style lore
        st.caption(f"_{config.styles[selected_style]}_")

        # Story Length
        selected_length = st.select_slider(
            "⏳ Story Length",
            options=list(config.lengths.keys()),
            value="Medium",
            help="Target depth and word count of the narrative."
        )
        _, _, length_desc = config.lengths[selected_length]
        st.caption(f"_{length_desc}_")

    # Optional Custom Twist / Premise
    custom_twist = st.text_area(
        "🕯️ Specific Premise or Dark Twist (Optional)",
        placeholder="e.g., The protagonist discovers that the emergency broadcast has been looping their own voice from ten minutes in the future.",
        max_chars=500,
        help="Add any specific element, cursed object, or twist you want the ghost to weave into the story."
    )

    # Advanced Settings Expander
    with st.expander("⚙️ Dark Alchemy (Model Parameters)", expanded=False):
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            creativity = st.slider(
                "Creativity / Temperature",
                min_value=0.2,
                max_value=1.0,
                value=config.default_temperature,
                step=0.05,
                help="Higher values yield more bizarre, unpredictable surrealism; lower values produce disciplined classical horror."
            )
        with col_param2:
            use_streaming = st.checkbox(
                "Stream Narrative (Live Typing)",
                value=True,
                help="Watch words materialize in real time as the local model generates them."
            )

    # Generate Button
    generate_col, _ = st.columns([0.35, 0.65])
    with generate_col:
        summon_clicked = st.button("👻 Summon My Ghost Story", use_container_width=True)

    # Trigger Generation
    if summon_clicked:
        # Determine effective setting & character
        final_setting = custom_setting_input if selected_setting == "Custom Setting..." else selected_setting
        final_character = custom_char_input if selected_character == "Custom Character..." else selected_character

        try:
            # Validate inputs first
            validated = st.session_state.generator.validate_inputs(
                setting=final_setting,
                character=final_character,
                horror_style=selected_style,
                length_category=selected_length,
                custom_prompt=custom_twist
            )

            # Check if model is available
            if not health["is_running"]:
                st.error("💀 Ollama is offline. Please launch `ollama serve` in PowerShell to awaken the AI.")
            elif not model_is_ready:
                st.error(f"💀 Model `{selected_model}` is not installed. Run `ollama pull {selected_model}`.")
            else:
                progress_container = st.empty()
                progress_container.info("🕯️ Awakening the spirit realm... Consulting the local model...")

                start_time = time.time()

                if use_streaming:
                    # Streaming generation
                    stream_generator = st.session_state.generator.generate_story_stream(
                        setting=validated["setting"],
                        character=validated["character"],
                        horror_style=validated["horror_style"],
                        length_category=validated["length_category"],
                        custom_prompt=validated["custom_prompt"],
                        model=selected_model,
                        temperature=creativity
                    )
                    
                    progress_container.empty()
                    story_placeholder = st.empty()
                    accumulated_text = ""
                    
                    with st.spinner("Inscribing the nightmare..."):
                        for token in stream_generator:
                            accumulated_text += token
                            story_placeholder.markdown(accumulated_text + "▌")
                    
                    story_placeholder.empty()
                    title, narrative = st.session_state.generator.extract_title_and_text(accumulated_text)
                    word_count = len(narrative.split())
                else:
                    # Synchronous generation
                    with st.spinner("Inscribing the nightmare onto parchment..."):
                        title, narrative, word_count = st.session_state.generator.generate_story(
                            setting=validated["setting"],
                            character=validated["character"],
                            horror_style=validated["horror_style"],
                            length_category=validated["length_category"],
                            custom_prompt=validated["custom_prompt"],
                            model=selected_model,
                            temperature=creativity
                        )
                    progress_container.empty()

                duration = round(time.time() - start_time, 2)

                # Store into session state
                st.session_state.current_story = {
                    "title": title,
                    "story_text": narrative,
                    "setting": validated["setting"],
                    "character": validated["character"],
                    "horror_style": validated["horror_style"],
                    "length_category": validated["length_category"],
                    "custom_prompt": validated["custom_prompt"],
                    "model_used": selected_model,
                    "word_count": word_count,
                    "duration_sec": duration,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.story_saved_flag = False
                st.toast("🕯️ The nightmare has materialized!", icon="👻")

        except StoryValidationError as ve:
            st.warning(f"⚠️ {str(ve)}")
        except OllamaTimeoutError as te:
            st.error(f"⏳ {str(te)}")
        except OllamaConnectionError as ce:
            st.error(f"🔌 {str(ce)}")
        except ModelNotFoundError as me:
            st.error(f"📦 {str(me)}")
        except Exception as e:
            st.error(f"💀 An unexpected horror occurred: {str(e)}")

    # Display Current Story if Available
    if st.session_state.current_story:
        story = st.session_state.current_story

        st.markdown(f"""
        <div class="story-card">
            <div class="story-title">{story['title']}</div>
            <div class="story-meta-row">
                <span class="story-badge badge-orange">🩸 {story['horror_style']}</span>
                <span class="story-badge badge-purple">🏚️ {story['setting']}</span>
                <span class="story-badge badge-gray">👤 {story['character']}</span>
                <span class="story-badge badge-gray">📖 {story['word_count']} words</span>
                <span class="story-badge badge-red">⚡ {story.get('duration_sec', 0)}s</span>
                <span class="story-badge badge-gray">🤖 {story['model_used']}</span>
            </div>
            <div class="story-body">{story['story_text']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Action Buttons
        col_act1, col_act2, col_act3, col_act4 = st.columns([0.25, 0.25, 0.25, 0.25])

        with col_act1:
            # Save to Database
            if st.session_state.story_saved_flag:
                st.button("✅ Saved in Grimoire", disabled=True, use_container_width=True)
            else:
                if st.button("💾 Save to Grimoire", use_container_width=True):
                    saved_rec = st.session_state.storage.save_story(
                        title=story["title"],
                        story_text=story["story_text"],
                        setting=story["setting"],
                        character=story["character"],
                        horror_style=story["horror_style"],
                        length_category=story["length_category"],
                        model_used=story["model_used"],
                        custom_prompt=story.get("custom_prompt", "")
                    )
                    st.session_state.story_saved_flag = True
                    st.toast(f"Saved story #{saved_rec.id} to your local Grimoire!", icon="📜")
                    st.rerun()

        with col_act2:
            # Download as .txt
            record_obj = StoryRecord(
                id=None,
                title=story["title"],
                story_text=story["story_text"],
                setting=story["setting"],
                character=story["character"],
                horror_style=story["horror_style"],
                length_category=story["length_category"],
                custom_prompt=story.get("custom_prompt", ""),
                model_used=story["model_used"],
                word_count=story["word_count"],
                created_at=story["created_at"]
            )
            export_content = record_obj.to_export_text()
            file_slug = "".join(c for c in story["title"] if c.isalnum() or c in (" ", "_")).rstrip()
            filename = f"GhostWriter_{file_slug.replace(' ', '_')}.txt"

            st.download_button(
                label="📥 Download (.txt)",
                data=export_content,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )

        with col_act3:
            # Re-summon / Variation
            if st.button("🔄 Summon Another Variation", use_container_width=True):
                st.session_state.current_story = None
                st.rerun()

        with col_act4:
            # Expand for Raw Text Copy
            with st.popover("📋 Copy Story"):
                st.text_area("Full Story Text", value=f"{story['title']}\n\n{story['story_text']}", height=200)
                st.caption("Press Ctrl+A, then Ctrl+C to copy.")


# =========================================================================
# TAB 2: THE HAUNTED GRIMOIRE (SAVED STORIES)
# =========================================================================
with tab_archive:
    st.markdown("### 📜 The Haunted Grimoire — Saved Tales")
    st.caption("All stories persisted locally in your offline SQLite repository (`data/ghostwriter.db`).")

    col_flt1, col_flt2, col_flt3 = st.columns([0.45, 0.35, 0.20])

    with col_flt1:
        search_kw = st.text_input("🔍 Search tales by keyword, title, or setting", placeholder="e.g., asylum, mirror, guard")

    with col_flt2:
        filter_style_choice = st.selectbox(
            "Filter by Horror Style",
            options=["All Styles"] + list(config.styles.keys()),
            index=0
        )

    with col_flt3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        only_favs = st.checkbox("⭐ Favorites Only", value=False)

    saved_stories = st.session_state.storage.get_all_stories(
        filter_style=filter_style_choice,
        search_query=search_kw,
        only_favorites=only_favs
    )

    if not saved_stories:
        st.info("🕸️ No spectral tales found matching your criteria. Inscribe your first story in the Generator tab!")
    else:
        st.markdown(f"**Found {len(saved_stories)} tales in the archive:**")

        for story in saved_stories:
            with st.container():
                st.markdown(f"""
                <div style="background:#13101d; border:1px solid #2e2445; border-radius:10px; padding:18px 22px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <h4 style="font-family:'Cinzel Decorative', serif; margin:0; color:#ffedd8;">
                            {'⭐ ' if story.is_favorite else ''}{story.title}
                        </h4>
                        <span style="font-size:0.8rem; color:#8e859e;">Inscribed: {story.created_at}</span>
                    </div>
                    <div style="margin:8px 0 12px 0;">
                        <span class="story-badge badge-orange">{story.horror_style}</span>
                        <span class="story-badge badge-purple">{story.setting}</span>
                        <span class="story-badge badge-gray">{story.character}</span>
                        <span class="story-badge badge-gray">{story.word_count} words</span>
                        <span class="story-badge badge-gray">🤖 {story.model_used}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"📖 Read '{story.title}'", expanded=False):
                    st.markdown(f"<div class='story-body'>{story.story_text}</div>", unsafe_allow_html=True)

                    st.markdown("---")
                    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([0.25, 0.25, 0.25, 0.25])

                    with btn_c1:
                        # Favorite toggle
                        star_label = "⭐ Remove Favorite" if story.is_favorite else "☆ Mark Favorite"
                        if st.button(star_label, key=f"fav_{story.id}"):
                            st.session_state.storage.toggle_favorite(story.id)
                            st.rerun()

                    with btn_c2:
                        # Download .txt
                        export_txt = story.to_export_text()
                        f_slug = "".join(c for c in story.title if c.isalnum() or c in (" ", "_")).rstrip()
                        st.download_button(
                            "📥 Download .txt",
                            data=export_txt,
                            file_name=f"GhostWriter_{f_slug}.txt",
                            mime="text/plain",
                            key=f"dl_{story.id}"
                        )

                    with btn_c3:
                        # Copy
                        with st.popover("📋 Copy Story", key=f"copy_pop_{story.id}"):
                            st.text_area("Prose", value=f"{story.title}\n\n{story.story_text}", height=180, key=f"ta_{story.id}")

                    with btn_c4:
                        # Delete with confirmation
                        confirm_del = st.checkbox("Confirm Delete", key=f"chk_del_{story.id}")
                        if st.button("🗑️ Delete Tale", key=f"del_{story.id}", disabled=not confirm_del):
                            st.session_state.storage.delete_story(story.id)
                            st.toast(f"Deleted tale #{story.id}", icon="🗑️")
                            st.rerun()


# =========================================================================
# TAB 3: OPEN AI MANIFESTO & PRIVACY
# =========================================================================
with tab_manifesto:
    st.markdown("### 🔮 Why Open AI & Local Models Matter")
    st.markdown("""
    **GhostWriter** was crafted for the **Hacktoberfest Open-Source AI Challenge: 'Ghost in the Machine'**.
    It demonstrates that creative fiction generation can run entirely locally without handing your private thoughts,
    intellectual property, or data to corporate cloud APIs.
    """)

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown("""
        #### 🛡️ Complete Privacy & Independence
        - **Zero Cloud Leakage:** Prompts never leave your computer.
        - **Immunity to Censorship:** No sudden corporate terms-of-service changes terminating your account.
        - **Forever Available:** GhostWriter continues generating stories even when your internet connection is down or during travel.
        """)

    with col_m2:
        st.markdown("""
        #### 💰 Economic Sovereignty & Zero Subscriptions
        - **No API Invoices:** Cloud LLM tokens cost money on every request; local open weights run on electricity you already pay for.
        - **Model Portability:** Switch freely between Qwen, Llama, and Gemma without refactoring your codebase.
        - **Verifiable Code:** No closed-source black boxes. You can audit every line of Python.
        """)

    st.markdown("---")
    st.markdown("#### ⚡ Hardware Requirements & Sizing")
    st.markdown("""
    | Model | Parameters | Download Size | Minimum VRAM / RAM | Recommendation |
    | :--- | :--- | :--- | :--- | :--- |
    | **Qwen 2.5 3B** | 3.09 Billion | ~1.9 GB | 4 GB VRAM / 8 GB RAM | **Best overall balance** of spine-chilling prose and rapid inference. |
    | **Llama 3.2 3B** | 3.21 Billion | ~2.0 GB | 4 GB VRAM / 8 GB RAM | Strong dialogue, fast pacing, low latency. |
    | **Qwen 2.5 1.5B** | 1.54 Billion | ~986 MB | 2 GB VRAM / 4 GB RAM | Ultra-fast on CPU or budget laptops. |
    | **Gemma 2 2B** | 2.61 Billion | ~1.6 GB | 3 GB VRAM / 6 GB RAM | Deeply atmospheric, rich vocabulary. |
    """)

    st.markdown("---")
    st.markdown("#### 📜 Licenses and Attribution")
    st.markdown("""
    - **GhostWriter Application:** Released under the **MIT License**. Free to inspect, fork, and remix.
    - **Ollama:** Open-source software released under the **MIT License**.
    - **Qwen2.5 Models:** Open-weight models created by Alibaba Cloud, released under the **Apache 2.0 License**.
    - **Llama 3.2 Models:** Open-weight models released under the **Llama 3.2 Community License Agreement**.
    - **Gemma 2 Models:** Open-weight models released under the **Gemma Terms of Use**.
    """)
