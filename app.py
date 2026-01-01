import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import time
import numpy as np
from collections import Counter

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Habit Enforcement System",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0f0f2e 100%);
        color: #e0e0e0;
        letter-spacing: 0.3px;
    }
    
    .main { background: rgba(0, 0, 0, 0) !important; }
    [data-testid="stAppViewContainer"] { 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0f0f2e 100%);
    }
    [data-testid="stSidebar"] { 
        background: rgba(15, 15, 46, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    h1, h2, h3 { font-family: 'Space Mono', monospace; letter-spacing: 1px; }
    h1 { color: #ff6b6b; font-size: 2.5rem; font-weight: 700; }
    h2 { color: #e0e0e0; font-size: 1.3rem; font-weight: 600; }
    h3 { color: #b8b8b8; font-size: 1rem; font-weight: 500; }
    
    /* VERDICT CARDS */
    .verdict-box {
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .verdict-good {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
        border: 2px solid #10b981;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.1);
    }
    
    .verdict-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%);
        border: 2px solid #f59e0b;
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.1);
    }
    
    .verdict-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.08) 100%);
        border: 2px solid #ef4444;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
        animation: pulse-critical 2s ease-in-out infinite;
    }
    
    .verdict-brutal {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.3) 0%, rgba(127, 29, 29, 0.1) 100%);
        border: 2px solid #991b1b;
        box-shadow: 0 8px 32px rgba(127, 29, 29, 0.2);
        animation: pulse-critical 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse-critical {
        0%, 100% { box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15); }
        50% { box-shadow: 0 8px 40px rgba(239, 68, 68, 0.3); }
    }
    
    /* HABIT CARDS */
    .habit-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .habit-card:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.04) 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
    }
    
    .habit-focus {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%);
        border: 2px solid #6366f1;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
    }
    
    .habit-blur {
        opacity: 0.35;
        pointer-events: none;
    }
    
    .habit-warning {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(220, 38, 38, 0.03) 100%);
        border-left: 4px solid #dc2626;
        padding: 12px;
        border-radius: 8px;
        margin-top: 8px;
        color: #fca5a5;
        font-size: 0.9rem;
    }
    
    /* INTERVENTION BOX */
    .intervention-box {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.4) 0%, rgba(127, 29, 29, 0.15) 100%);
        border: 3px solid #991b1b;
        border-radius: 16px;
        padding: 32px;
        margin: 20px 0;
        box-shadow: 0 12px 48px rgba(127, 29, 29, 0.2);
        text-align: center;
        animation: pulse-critical 1.2s ease-in-out infinite;
    }
    
    .intervention-box h2 {
        color: #fca5a5;
        margin-bottom: 16px;
        letter-spacing: 2px;
    }
    
    /* METRICS */
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.02) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.15);
    }
    
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #6366f1;
        line-height: 1;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #999;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* STREAK DANGER */
    .streak-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%);
        border: 1px dashed #ef4444;
        padding: 12px;
        border-radius: 8px;
        color: #fca5a5;
        margin: 8px 0;
    }
    
    /* FROZEN STATE */
    .frozen-notice {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    
    .frozen-notice h3 { color: #60a5fa; }
    .frozen-notice p { color: #93c5fd; margin-top: 8px; }
    
    /* PROFILE BADGE */
    .profile-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(168, 85, 247, 0.05) 100%);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 20px;
        padding: 8px 16px;
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        color: #d8b4fe;
        margin: 8px 0;
        letter-spacing: 1px;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }
    
    .stButton > button:disabled {
        background: rgba(99, 102, 241, 0.3);
        color: #999;
        cursor: not-allowed;
        box-shadow: none;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA MANAGEMENT ====================
DATA_FILE = "habits_enforcement.json"

def init_session_state():
    if 'habits' not in st.session_state:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.habits = data.get('habits', [])
                st.session_state.total_points = data.get('total_points', 0)
        else:
            st.session_state.habits = []
            st.session_state.total_points = 0

init_session_state()

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'habits': st.session_state.habits,
            'total_points': st.session_state.total_points
        }, f, indent=2)

# ==================== ADVANCED ANALYTICS FUNCTIONS ====================

def get_today():
    return datetime.now().date().strftime('%Y-%m-%d')

def get_week_start():
    today = datetime.now().date()
    return (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')

def get_month_start():
    today = datetime.now().date()
    return today.replace(day=1).strftime('%Y-%m-%d')

def calculate_streak():
    """Calculate current and longest streak from completed_dates"""
    if not st.session_state.habits:
        return 0, 0
    
    all_completed_dates = []
    for habit in st.session_state.habits:
        for date_str in habit['completed_dates']:
            try:
                all_completed_dates.append(datetime.strptime(date_str, '%Y-%m-%d').date())
            except:
                pass
    
    if not all_completed_dates:
        return 0, 0
    
    all_completed_dates = sorted(set(all_completed_dates), reverse=True)
    
    today = datetime.now().date()
    current_streak = 0
    
    if all_completed_dates[0] == today or all_completed_dates[0] == today - timedelta(days=1):
        current_streak = 1
        for i in range(1, len(all_completed_dates)):
            if all_completed_dates[i] == all_completed_dates[i-1] - timedelta(days=1):
                current_streak += 1
            else:
                break
    
    longest_streak = 1
    temp_streak = 1
    for i in range(1, len(all_completed_dates)):
        if all_completed_dates[i] == all_completed_dates[i-1] - timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return current_streak, longest_streak

def get_today_status():
    """Get today's completion status"""
    today = get_today()
    completed = 0
    total = 0
    
    for habit in st.session_state.habits:
        if today in habit['completed_dates'] or today in habit['missed_dates']:
            total += 1
            if today in habit['completed_dates']:
                completed += 1
    
    return completed, total

def calculate_daily_verdict():
    """Generate harsh verdict based on last 3 days"""
    today = datetime.now().date()
    last_3_days = [today - timedelta(days=i) for i in range(3)]
    
    all_attempts = []
    for habit in st.session_state.habits:
        for day in last_3_days:
            day_str = day.strftime('%Y-%m-%d')
            if day_str in habit['completed_dates']:
                all_attempts.append(True)
            elif day_str in habit['missed_dates']:
                all_attempts.append(False)
    
    if not all_attempts:
        return {
            "type": "CRITICAL",
            "message": "🚨 No activity in 3 days. You've already quit.",
            "emoji": "🚨"
        }
    
    rate = sum(all_attempts) / len(all_attempts)
    
    current_streak, _ = calculate_streak()
    
    recent = all_attempts[-5:] if len(all_attempts) >= 5 else all_attempts
    fails_in_recent = sum(1 for x in recent if not x)
    
    if fails_in_recent >= 3:
        return {
            "type": "BRUTAL",
            "message": "🔥 You've failed 3+ times. This is a pattern, not a bad day.",
            "emoji": "🔥"
        }
    
    if rate < 0.3:
        return {
            "type": "CRITICAL",
            "message": "🚨 70% failure rate. Stop adding habits. Fix existing ones.",
            "emoji": "🚨"
        }
    
    if rate < 0.6:
        return {
            "type": "WARNING",
            "message": f"⚠️ Weak (60% failing). Your {current_streak}-day streak is at risk.",
            "emoji": "⚠️"
        }
    
    if current_streak > 0 and rate >= 0.8:
        return {
            "type": "GOOD",
            "message": f"✓ You did what you said. {current_streak}-day streak alive. Don't slip.",
            "emoji": "✓"
        }
    
    if rate >= 0.8:
        return {
            "type": "GOOD",
            "message": "✓ Strong performance. Build this into a streak.",
            "emoji": "✓"
        }
    
    return {
        "type": "WARNING",
        "message": "⚠️ One more slip breaks your streak.",
        "emoji": "⚠️"
    }

def should_freeze_habits():
    """Check if new habits should be frozen"""
    if len(st.session_state.habits) < 2:
        return False
    
    total_completed = sum(len(h['completed_dates']) for h in st.session_state.habits)
    total_attempts = sum(len(h['completed_dates']) + len(h['missed_dates']) for h in st.session_state.habits)
    
    if total_attempts == 0:
        return False
    
    completion_rate = total_completed / total_attempts
    return completion_rate < 0.3

def calculate_weekly_performance():
    """Calculate performance for last 7 days"""
    today = datetime.now().date()
    week_start = today - timedelta(days=7)
    
    week_completed = 0
    week_total = 0
    
    for habit in st.session_state.habits:
        for date_str in habit['completed_dates']:
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
                if week_start <= d <= today:
                    week_completed += 1
                    week_total += 1
            except:
                pass
        
        for date_str in habit['missed_dates']:
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
                if week_start <= d <= today:
                    week_total += 1
            except:
                pass
    
    if week_total == 0:
        return 0
    
    return (week_completed / week_total) * 100

def calculate_monthly_performance():
    """Calculate performance for last 30 days"""
    today = datetime.now().date()
    month_start = today - timedelta(days=30)
    
    month_completed = 0
    month_total = 0
    
    for habit in st.session_state.habits:
        for date_str in habit['completed_dates']:
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
                if month_start <= d <= today:
                    month_completed += 1
                    month_total += 1
            except:
                pass
        
        for date_str in habit['missed_dates']:
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
                if month_start <= d <= today:
                    month_total += 1
            except:
                pass
    
    if month_total == 0:
        return 0
    
    return (month_completed / month_total) * 100

def detect_personality():
    """Detect user's habit personality"""
    if not st.session_state.habits:
        return "Uninitialized", "📋"
    
    total = len(st.session_state.habits)
    completed = sum(len(h['completed_dates']) for h in st.session_state.habits)
    missed = sum(len(h['missed_dates']) for h in st.session_state.habits)
    
    if total > 5 and completed < total * 0.2:
        return "Starter", "🚀"
    
    hard_completed = sum(len(h['completed_dates']) for h in st.session_state.habits if h['difficulty'] == 'Hard')
    hard_total = sum(len(h['completed_dates']) + len(h['missed_dates']) for h in st.session_state.habits if h['difficulty'] == 'Hard')
    
    if hard_total > 0 and hard_completed / hard_total < 0.3:
        return "Avoider", "🙈"
    
    attempt_lengths = []
    for h in st.session_state.habits:
        attempts = len(h['completed_dates']) + len(h['missed_dates'])
        if attempts > 0:
            attempt_lengths.append(attempts)
    
    if attempt_lengths and np.median(attempt_lengths) < 3:
        return "Quitter", "🛑"
    
    completion_rates = []
    for h in st.session_state.habits:
        total_h = len(h['completed_dates']) + len(h['missed_dates'])
        if total_h > 0:
            completion_rates.append(len(h['completed_dates']) / total_h)
    
    if completion_rates and np.std(completion_rates) > 0.35:
        return "Sprinter", "⚡"
    
    if completed > missed and completed > total * 0.6:
        return "Finisher", "🏆"
    
    return "Developing", "🔄"

def get_focus_habit():
    """Identify the habit breaking the user"""
    if not st.session_state.habits:
        return None
    
    worst_habit = None
    worst_rate = -1
    
    for habit in st.session_state.habits:
        total = len(habit['completed_dates']) + len(habit['missed_dates'])
        if total > 0:
            miss_rate = len(habit['missed_dates']) / total
            if miss_rate > worst_rate and miss_rate > 0.4:
                worst_rate = miss_rate
                worst_habit = habit
    
    return worst_habit

def check_intervention():
    """Check if user should enter intervention mode"""
    weekly_perf = calculate_weekly_performance()
    return weekly_perf < 40

def get_level():
    """Get current level"""
    points = st.session_state.total_points
    
    if points >= 1000:
        return {"name": "Legendary", "icon": "👑", "color": "#fbbf24"}
    elif points >= 600:
        return {"name": "Elite", "icon": "💎", "color": "#a855f7"}
    elif points >= 300:
        return {"name": "Discipline", "icon": "🎯", "color": "#6366f1"}
    elif points >= 100:
        return {"name": "Consistent", "icon": "⚡", "color": "#10b981"}
    else:
        return {"name": "Beginner", "icon": "🌱", "color": "#999"}

def get_best_day():
    """Find the day user succeeds most"""
    day_completions = Counter()
    for habit in st.session_state.habits:
        for date_str in habit['completed_dates']:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                day = date.strftime('%A')
                day_completions[day] += 1
            except:
                pass
    
    if day_completions:
        return day_completions.most_common(1)[0][0]
    return None

def get_worst_day():
    """Find the day user fails most"""
    day_failures = Counter()
    for habit in st.session_state.habits:
        for date_str in habit['missed_dates']:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                day = date.strftime('%A')
                day_failures[day] += 1
            except:
                pass
    
    if day_failures:
        return day_failures.most_common(1)[0][0]
    return None

def calculate_daily_completion_trend():
    """Calculate completion trend for last 7 days"""
    today = datetime.now().date()
    trend = {}
    
    for i in range(7):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        
        day_completed = 0
        day_total = 0
        
        for habit in st.session_state.habits:
            if day_str in habit['completed_dates']:
                day_completed += 1
                day_total += 1
            elif day_str in habit['missed_dates']:
                day_total += 1
        
        if day_total > 0:
            trend[day.strftime('%a')] = (day_completed / day_total) * 100
        else:
            trend[day.strftime('%a')] = 0
    
    return dict(reversed(list(trend.items())))

def get_habit_momentum(habit):
    """Calculate if habit is rising, stable, or falling"""
    total_attempts = len(habit['completed_dates']) + len(habit['missed_dates'])
    if total_attempts < 3:
        return "📊 New"
    
    all_dates = []
    for date_str in habit['completed_dates']:
        try:
            all_dates.append((datetime.strptime(date_str, '%Y-%m-%d'), True))
        except:
            pass
    
    for date_str in habit['missed_dates']:
        try:
            all_dates.append((datetime.strptime(date_str, '%Y-%m-%d'), False))
        except:
            pass
    
    all_dates.sort(reverse=True)
    recent_attempts = [completed for _, completed in all_dates[:5]]
    
    if len(recent_attempts) >= 3:
        recent_rate = sum(recent_attempts[-3:]) / 3
        older_rate = sum(recent_attempts[:3]) / 3 if len(recent_attempts) >= 3 else recent_rate
        
        if recent_rate > older_rate + 0.2:
            return "📈 Rising"
        elif recent_rate < older_rate - 0.2:
            return "📉 Falling"
    
    return "➡️ Stable"

def estimate_next_level():
    """Calculate points needed for next level"""
    points = st.session_state.total_points
    level = get_level()
    
    levels = [0, 100, 300, 600, 1000]
    current_idx = levels.index(level['color'].replace('#', '').split()[0] or 0)
    
    if current_idx < len(levels) - 1:
        next_threshold = levels[current_idx + 1]
        points_needed = next_threshold - points
        return max(0, points_needed)
    
    return 0

def get_habit_breakdown():
    """Get breakdown of habits by difficulty"""
    easy = sum(1 for h in st.session_state.habits if h['difficulty'] == 'Easy')
    medium = sum(1 for h in st.session_state.habits if h['difficulty'] == 'Medium')
    hard = sum(1 for h in st.session_state.habits if h['difficulty'] == 'Hard')
    
    return {"Easy": easy, "Medium": medium, "Hard": hard}

def calculate_difficulty_completion_rate():
    """Calculate completion rate by difficulty"""
    rates = {}
    
    for difficulty in ["Easy", "Medium", "Hard"]:
        habits_with_diff = [h for h in st.session_state.habits if h['difficulty'] == difficulty]
        if not habits_with_diff:
            rates[difficulty] = 0
        else:
            total_all = sum(len(h['completed_dates']) + len(h['missed_dates']) for h in habits_with_diff)
            total_completed = sum(len(h['completed_dates']) for h in habits_with_diff)
            rates[difficulty] = (total_completed / total_all * 100) if total_all > 0 else 0
    
    return rates

def get_consistency_score():
    """Calculate advanced consistency score (0-100)"""
    if not st.session_state.habits:
        return 0
    
    weekly_perf = calculate_weekly_performance()
    monthly_perf = calculate_monthly_performance()
    current_streak, _ = calculate_streak()
    
    consistency = (weekly_perf * 0.6) + (monthly_perf * 0.3) + min(current_streak * 5, 20)
    
    return max(0, min(100, consistency))

# ==================== UI RENDERING FUNCTIONS ====================

def render_verdict_card(verdict):
    """Render the daily verdict"""
    color_map = {
        "GOOD": "verdict-good",
        "WARNING": "verdict-warning",
        "CRITICAL": "verdict-critical",
        "BRUTAL": "verdict-brutal"
    }
    
    st.markdown(f"""
    <div class='{color_map.get(verdict['type'], 'verdict-warning')}'>
        <h2>TODAY'S VERDICT</h2>
        <p style='font-size: 1.1rem; margin-top: 12px; line-height: 1.6;'>{verdict['message']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_habit_card(habit, idx):
    """Render individual habit card"""
    today = get_today()
    is_completed_today = today in habit['completed_dates']
    
    total_attempts = len(habit['completed_dates']) + len(habit['missed_dates'])
    completion_pct = (len(habit['completed_dates']) / total_attempts * 100) if total_attempts > 0 else 0
    
    diff_colors = {
        "Easy": "#10b981",
        "Medium": "#f59e0b",
        "Hard": "#ef4444"
    }
    
    status_icon = "✓" if is_completed_today else "◯"
    momentum = get_habit_momentum(habit)
    
    st.markdown(f"""
    <div class="habit-card">
        <div style='flex: 1;'>
            <div style='display: flex; gap: 16px; align-items: center;'>
                <span style='font-size: 1.5rem; font-weight: 700; color: {"#10b981" if is_completed_today else "#999"};'>{status_icon}</span>
                <div style='flex: 1;'>
                    <div style='font-weight: 600; font-size: 1rem;'>{habit['name']}</div>
                    <div style='font-size: 0.85rem; color: #999; margin-top: 4px;'>
                        {momentum} • {completion_pct:.0f}% • {len(habit['completed_dates'])}/{total_attempts} • <span style='color: {diff_colors.get(habit['difficulty'], "#999")};'>{habit['difficulty']}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Done", key=f"complete_{idx}", use_container_width=True):
            if today not in habit['completed_dates']:
                habit['completed_dates'].append(today)
                if today in habit['missed_dates']:
                    habit['missed_dates'].remove(today)
                
                points_map = {"Easy": 5, "Medium": 10, "Hard": 20}
                st.session_state.total_points += points_map[habit['difficulty']]
                save_data()
                st.rerun()
    
    with col2:
        if st.button("✗ Miss", key=f"miss_{idx}", use_container_width=True):
            if today not in habit['missed_dates']:
                habit['missed_dates'].append(today)
                if today in habit['completed_dates']:
                    habit['completed_dates'].remove(today)
                
                points_map = {"Easy": -2, "Medium": -5, "Hard": -10}
                st.session_state.total_points = max(0, st.session_state.total_points + points_map[habit['difficulty']])
                save_data()
                st.rerun()

# ==================== MAIN APP ====================

st.markdown("<h1 style='text-align: center;'>⚔️ HABIT ENFORCEMENT SYSTEM</h1>", unsafe_allow_html=True)

intervention_active = check_intervention()

if intervention_active:
    st.markdown("""
    <div class='intervention-box'>
        <h2>🚨 INTERVENTION MODE ACTIVE 🚨</h2>
        <p style='font-size: 1.1rem; margin: 16px 0; color: #fca5a5;'>Your weekly completion rate is below 40%.</p>
        <div style='background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin: 16px 0; text-align: left;'>
            <p style='color: #60a5fa; font-weight: 600; margin-bottom: 8px;'>Recovery Plan:</p>
            <p style='color: #ccc; line-height: 1.8;'>
                1. Complete ONE habit 7 days straight<br/>
                2. No new habits allowed<br/>
                3. System unlocks when successful
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    verdict = calculate_daily_verdict()
    render_verdict_card(verdict)

st.markdown("---")

completed_today, total_today = get_today_status()
current_streak, longest_streak = calculate_streak()
consistency = get_consistency_score()

summary_text = f"**Today: {completed_today} completed • {max(0, total_today - completed_today)} avoided • Streak: {current_streak} days • Consistency: {consistency:.0f}%**"

st.markdown(f"<p style='text-align: center; font-size: 1.1rem; color: #e0e0e0;'>{summary_text}</p>", unsafe_allow_html=True)

st.markdown("---")

personality, personality_emoji = detect_personality()
st.markdown(f"""
<div style='text-align: center;'>
    <p style='color: #999; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Your Habit Personality</p>
    <div class='profile-badge'>{personality_emoji} {personality}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Points</div>
        <div class='metric-value'>{st.session_state.total_points}</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 8px;'>{get_level()['icon']} {get_level()['name']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Total</div>
        <div class='metric-value'>{len(st.session_state.habits)}</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 8px;'>Habits</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    completion_pct = (completed_today / total_today * 100) if total_today > 0 else 0
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Today</div>
        <div class='metric-value'>{completion_pct:.0f}%</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 8px;'>Complete</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Streak</div>
        <div class='metric-value'>{current_streak}</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 8px;'>Days</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Consistency</div>
        <div class='metric-value'>{consistency:.0f}</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 8px;'>Score</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Status")
    
    level = get_level()
    st.markdown(f"#### {level['icon']} {level['name']}")
    st.markdown(f"**{st.session_state.total_points} points**")
    
    st.divider()
    
    st.markdown("### Performance")
    
    total_all = sum(len(h['completed_dates']) + len(h['missed_dates']) for h in st.session_state.habits)
    total_done = sum(len(h['completed_dates']) for h in st.session_state.habits)
    
    if total_all > 0:
        overall_rate = (total_done / total_all) * 100
        st.metric("Overall Rate", f"{overall_rate:.0f}%")
        st.metric("Weekly", f"{calculate_weekly_performance():.0f}%")
        st.metric("Monthly", f"{calculate_monthly_performance():.0f}%")
    
    st.divider()
    
    st.markdown("### Focus Target")
    focus = get_focus_habit()
    if focus:
        st.markdown(f"**{focus['name']}**")
        focus_total = len(focus['completed_dates']) + len(focus['missed_dates'])
        focus_rate = (len(focus['completed_dates']) / focus_total * 100) if focus_total > 0 else 0
        st.metric("Rate", f"{focus_rate:.0f}%")
        st.error("Fix this first.")
    
    st.divider()
    
    if current_streak > 0 and current_streak < 3:
        st.markdown("""
        <div class='streak-danger'>
            ⚠️ Your streak is fragile. One miss breaks it.
        </div>
        """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Habits", "📊 Analytics", "📈 Trends", "📋 Reality"])

with tab1:
    if intervention_active:
        st.error("🔒 INTERVENTION MODE: Only focus habit available")
        focus = get_focus_habit()
        if focus:
            st.subheader(focus['name'])
            render_habit_card(focus, st.session_state.habits.index(focus))
    else:
        st.markdown("### Add Habit")
        
        if should_freeze_habits():
            st.markdown("""
            <div class='frozen-notice'>
                <h3>🔒 HABIT FREEZE ACTIVE</h3>
                <p>You don't need new habits. You need discipline.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1])
            
            with col1:
                name = st.text_input("Name", label_visibility="collapsed", placeholder="Habit name")
            with col2:
                htype = st.selectbox("Type", ["Daily", "Weekly"], label_visibility="collapsed")
            with col3:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], label_visibility="collapsed")
            with col4:
                created = st.date_input("Date", value=datetime.now(), label_visibility="collapsed")
            with col5:
                if st.button("Add", use_container_width=True):
                    if name:
                        st.session_state.habits.append({
                            "id": int(time.time() * 1000),
                            "name": name,
                            "type": htype,
                            "difficulty": difficulty,
                            "created_date": created.strftime('%Y-%m-%d'),
                            "completed_dates": [],
                            "missed_dates": []
                        })
                        save_data()
                        st.rerun()
        
        st.divider()
        
        if st.session_state.habits:
            st.markdown("### Your Habits")
            
            for idx, habit in enumerate(st.session_state.habits):
                render_habit_card(habit, idx)
        else:
            st.info("No habits yet. Add one to start.")

with tab2:
    st.markdown("### Analytics")
    
    if st.session_state.habits:
        current_streak, _ = calculate_streak()
        total_all = sum(len(h['completed_dates']) + len(h['missed_dates']) for h in st.session_state.habits)
        total_done = sum(len(h['completed_dates']) for h in st.session_state.habits)
        overall_rate = (total_done / total_all) if total_all > 0 else 0
        
        can_view = current_streak >= 3 or overall_rate >= 0.6
        
        if not can_view:
            st.warning("📊 Analytics unlock when: 3+ day streak OR 60%+ completion")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall %", f"{overall_rate*100:.0f}%")
            with col2:
                st.metric("Weekly %", f"{calculate_weekly_performance():.0f}%")
            with col3:
                st.metric("Monthly %", f"{calculate_monthly_performance():.0f}%")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                diff_rates = calculate_difficulty_completion_rate()
                
                fig1 = go.Figure(data=[
                    go.Bar(x=list(diff_rates.keys()), y=list(diff_rates.values()), marker=dict(color=['#10b981', '#f59e0b', '#ef4444']))
                ])
                fig1.update_layout(
                    title="By Difficulty",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e0e0e0'),
                    height=350
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                done_count = completed_today
                missed_count = max(0, total_today - completed_today)
                
                fig2 = go.Figure(data=[go.Pie(
                    labels=['Done', 'Missed'],
                    values=[done_count, missed_count],
                    hole=0.3,
                    marker=dict(colors=['#10b981', '#ef4444'])
                )])
                fig2.update_layout(
                    title="Today",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e0e0e0'),
                    height=350
                )
                st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("### 7-Day Trend")
    
    if st.session_state.habits:
        trend = calculate_daily_completion_trend()
        
        fig_trend = go.Figure(data=[
            go.Bar(x=list(trend.keys()), y=list(trend.values()), marker=dict(color='#6366f1'))
        ])
        fig_trend.update_layout(
            title="Daily Completion % (Last 7 Days)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.divider()
        
        best_day = get_best_day()
        worst_day = get_worst_day()
        
        col1, col2 = st.columns(2)
        with col1:
            if best_day:
                st.success(f"✓ Best day: **{best_day}** (luck, not discipline)")
        with col2:
            if worst_day:
                st.error(f"✗ Worst day: **{worst_day}** (pattern to fix)")

with tab4:
    st.markdown("### Reality Check")
    
    personality, emoji = detect_personality()
    st.markdown(f"#### {emoji} You are a **{personality}**")
    
    personality_meanings = {
        "Starter": "You start many but finish few. You confuse enthusiasm with discipline.",
        "Avoider": "You avoid hard habits. You'll never grow doing only easy things.",
        "Quitter": "You give up after 2-3 days. You're failing yourself, not habits.",
        "Sprinter": "You're inconsistent. You need systems, not motivation.",
        "Finisher": "You complete what you start. Build on this.",
        "Developing": "Your patterns are still forming. Be consistent.",
        "Uninitialized": "No data yet. Start tracking to get feedback."
    }
    
    st.markdown(f"> {personality_meanings.get(personality, '')}")
    
    st.divider()
    
    st.markdown("### Facts")
    
    total_habits = len(st.session_state.habits)
    total_completed = sum(len(h['completed_dates']) for h in st.session_state.habits)
    total_missed = sum(len(h['missed_dates']) for h in st.session_state.habits)
    
    st.markdown(f"""
    - **{total_habits}** habits started
    - **{total_completed}** times completed
    - **{total_missed}** times failed
    """)
    
    if total_completed + total_missed > 0:
        fail_rate = (total_missed / (total_completed + total_missed)) * 100
        st.markdown(f"- **{fail_rate:.0f}%** failure rate")
    
    breakdown = get_habit_breakdown()
    st.markdown(f"- Distribution: **{breakdown['Easy']} Easy** • **{breakdown['Medium']} Medium** • **{breakdown['Hard']} Hard**")

st.divider()
st.markdown("<center style='color: #666; font-size: 0.85rem;'>Honesty > Motivation • Behavior > Feelings</center>", unsafe_allow_html=True)