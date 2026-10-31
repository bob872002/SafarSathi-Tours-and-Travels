
import streamlit as st
import mysql.connector
from datetime import date, datetime, time
from pathlib import Path
import base64
import re

from db import get_connection
from security import hash_password, verify_password


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="SafarSathi Tours & Travels",
    page_icon="✈️",
    layout="wide",
)


# ---------------- DATABASE HELPERS ----------------

def fetch_all(query, params=()):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def execute_query(query, params=()):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_packages():
    return fetch_all(
        """
        SELECT id, title, destination, description,
               price, duration_days
        FROM packages
        WHERE active = TRUE
        ORDER BY id
        """
    )


# ---------------- SESSION STATE ----------------

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Home"


def navigate_to(page):
    """Update navigation widget state safely from a Streamlit callback."""
    st.session_state.page = page
    if st.session_state.get("user") is None:
        st.session_state["public_navigation"] = page
    else:
        st.session_state["logged_in_navigation"] = page

def open_package_details(package_id):
    st.session_state["detail_package_id"] = package_id
    navigate_to("Tour Packages")

def back_to_packages():
    st.session_state.pop("detail_package_id", None)
    navigate_to("Tour Packages")


# ---------------- VISUAL THEME ----------------

APP_DIR = Path(__file__).resolve().parent
IMAGE_ROOT = APP_DIR / "images"


def image_to_data_uri(path):
    """Encode a local image for use as a CSS background."""
    try:
        suffix = path.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/webp" if suffix == ".webp" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""


hero_path = IMAGE_ROOT / "background.jpg"
hero_uri = image_to_data_uri(hero_path) if hero_path.is_file() else ""
hero_css = f'url("{hero_uri}")' if hero_uri else "linear-gradient(120deg, #0b477c, #43a5dc)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {{ --navy:#104d82; --blue:#1769aa; --orange:#ff9418; --pale:#edf7ff; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: linear-gradient(180deg,#f4faff 0%,#ffffff 50%,#edf7ff 100%); color:#123b63; }}
[data-testid="stHeader"] {{ background:rgba(255,255,255,.88); }}
.block-container {{ max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }}
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#e8f5ff,#ffffff); border-right:1px solid #d6eaff; }}
[data-testid="stSidebar"] * {{ color:#104d82; }}
.stButton > button, .stFormSubmitButton > button {{ border-radius:999px; border:0; background:linear-gradient(90deg,#ff8a00,#ffad24); color:white; font-weight:700; padding:.55rem 1.15rem; box-shadow:0 5px 14px #ff9a1f33; }}
.stButton > button:hover, .stFormSubmitButton > button:hover {{ background:#ed7900; color:white; border:0; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border:1px solid #d8ebfa; border-radius:18px; box-shadow:0 5px 20px #145b8b0d; background:rgba(255,255,255,.9); }}
h1,h2,h3 {{ color:#104d82 !important; letter-spacing:-.025em; }}
[data-testid="stMetric"] {{ background:#f2f9ff; border:1px solid #d9edff; padding:14px; border-radius:14px; }}
.hero {{ background-image:linear-gradient(90deg,rgba(4,38,68,.78),rgba(5,53,86,.28) 58%,rgba(5,53,86,.06)), {hero_css}; background-size:cover; background-position:center; min-height:280px; border-radius:24px; padding:38px 42px; display:flex; flex-direction:column; justify-content:center; color:white; box-shadow:0 12px 35px #174e7b22; margin-bottom:20px; }}
.hero h1 {{ color:#fff !important; font-size:clamp(2.3rem,4.3vw,4rem); line-height:1.02; margin:0 0 12px 0; font-weight:800; }}
.hero p {{ color:#fff; font-size:1.08rem; max-width:610px; margin:0 0 18px 0; }}
.hero .accent {{ color:#ff9b16; }}
.feature {{ border:1px solid #dceeff; border-radius:16px; padding:15px 12px; background:#fff; height:100%; box-shadow:0 4px 16px #1c60900b; }}
.feature strong {{ color:#104d82; }}
.small-muted {{ color:#5b7892; font-size:.9rem; }}
.price {{ color:#075ca2; font-size:1.55rem; font-weight:800; }}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

brand_col, tagline_col = st.columns([1, 2])
with brand_col:
    st.markdown("<div style='font-size:1.7rem;font-weight:800;color:#104d82'>✈️ Safar<span style='color:#ff9418'>Sathi</span></div><div style='color:#5b7892;font-size:.82rem;margin-top:-5px'>TOURS & TRAVELS</div>", unsafe_allow_html=True)
with tagline_col:
    st.markdown("<div style='text-align:right;padding-top:10px;color:#54728d'>Better Places. Bigger Dreams. &nbsp; 🌍</div>", unsafe_allow_html=True)
st.markdown("<hr style='border:0;border-top:1px solid #d9ecfa;margin:12px 0 22px'>", unsafe_allow_html=True)


# ---------------- REGISTER ----------------

def show_register():
    st.header("Create Your Account")

    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address").strip().lower()
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Register",
            use_container_width=True,
        )

    if submitted:
        if not name.strip() or not email or not password:
            st.error("Please fill in all required fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        if len(password) < 8:
            st.error("Password must be at least 8 characters.")
            return

        try:
            execute_query(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'customer')
                """,
                (name.strip(), email, hash_password(password)),
            )

            st.success("Account created! Please log in.")
            st.session_state.page = "Login"
            st.rerun()

        except mysql.connector.IntegrityError:
            st.error("This email is already registered.")

        except mysql.connector.Error as error:
            st.error(f"Database error: {error}")


# ---------------- LOGIN ----------------

def show_login():
    st.header("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email Address").strip().lower()
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:
        if not email or not password:
            st.error("Enter your email and password.")
            return

        try:
            users = fetch_all(
                """
                SELECT id, name, email, password_hash, role
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email,),
            )

            if users and verify_password(
                password, users[0]["password_hash"]
            ):
                user = users[0]

                st.session_state.user = {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                }

                st.session_state.page = "Home"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect email or password.")

        except mysql.connector.Error as error:
            st.error(f"Database error: {error}")


# ---------------- HOME ----------------

def show_home():
    st.markdown("""
    <section class="hero">
      <h1>Welcome to<br>Safar<span class="accent">Sathi!</span> ✈</h1>
      <p>Discover beautiful destinations, explore our tour packages, and plan your next memorable journey with us.</p>
    </section>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("✈️", "Best Tour Packages", "Curated for amazing experiences"),
        ("📍", "Amazing Destinations", "Explore the world with us"),
        ("🛡️", "Safe & Secure Travel", "Your safety is our priority"),
        ("🎧", "Friendly Support", "Here to help you plan"),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f'<div class="feature"><div style="font-size:1.7rem">{icon}</div><strong>{title}</strong><div class="small-muted">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    title_col, link_col = st.columns([4, 1])
    with title_col:
        st.markdown("## 🧳 Our Tour Packages")
        st.markdown("Discover amazing destinations with our specially curated travel experiences.")
    with link_col:
        st.markdown("<div style='padding-top:18px'></div>", unsafe_allow_html=True)
        st.button("View Packages →", use_container_width=True, key="home_view_packages", on_click=navigate_to, args=("Tour Packages",))

    try:
        packages = get_packages()
    except mysql.connector.Error:
        packages = []
    if packages:
        cols = st.columns(min(3, len(packages)))
        for i, package in enumerate(packages[:3]):
            with cols[i % len(cols)]:
                with st.container(border=True):
                    images = get_package_images(package["destination"])
                    if images:
                        st.image(images[0], use_container_width=True)
                    else:
                        st.markdown("<div style='background:linear-gradient(135deg,#d7efff,#8bc8ee);border-radius:12px;padding:35px 8px;text-align:center;font-size:2.6rem'>🏞️</div>", unsafe_allow_html=True)
                    st.markdown(f"### {package['title']}")
                    st.caption(f"📍 {package['destination']}  ·  🗓️ {package['duration_days']} days")
                    st.write((package["description"] or "Explore this tour.")[:135])
                    st.markdown(f'<div class="price">₹{package["price"]:,}</div><div class="small-muted">per person</div>', unsafe_allow_html=True)
                    st.button("Explore this destination →", key=f"home_pkg_{package['id']}", use_container_width=True, on_click=open_package_details, args=(package["id"],))
    else:
        # Keep the landing page attractive even if the database has no active packages.
        c1, c2, c3 = st.columns(3)
        for col, name, icon, desc in [
            (c1, "Jaipur", "🏰", "Royal palaces, forts and heritage"),
            (c2, "Goa", "🏖️", "Golden beaches and sunsets"),
            (c3, "Manali", "🏔️", "Snow-capped mountains and nature"),
        ]:
            with col:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:3rem;text-align:center;padding:18px'>{icon}</div><h3 style='text-align:center'>{name}</h3><p style='text-align:center'>{desc}</p>", unsafe_allow_html=True)

    st.markdown("## 💙 Why Choose SafarSathi?")
    b1, b2, b3, b4 = st.columns(4)
    for col, icon, title, desc in [
        (b1, "🤝", "Trusted Service", "Travel planning made simple"),
        (b2, "₹", "Great Value", "Packages for every budget"),
        (b3, "📅", "Easy Booking", "Simple booking requests"),
        (b4, "🎧", "Travel Support", "Help when you need it"),
    ]:
        with col:
            st.markdown(f'<div class="feature"><div style="font-size:1.5rem">{icon}</div><strong>{title}</strong><div class="small-muted">{desc}</div></div>', unsafe_allow_html=True)


# ---------------- TOUR PACKAGES ----------------

def destination_image_folder(destination):
    """Convert a destination to its matching local image folder."""
    text = str(destination or "").strip().lower()
    for known in ("jaipur", "goa", "manali", "ladakh"):
        if known in text:
            return known
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "destination"


def get_package_images(destination):
    """Find up to five local photos in images/<destination>/."""
    folder = destination_image_folder(destination)
    image_dir = IMAGE_ROOT / folder
    images = []
    for number in range(1, 6):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = image_dir / f"{folder}{number}{ext}"
            if candidate.is_file():
                images.append(str(candidate))
                break
    return images


def show_packages():
    try:
        packages = get_packages()
        if not packages:
            st.warning("No active packages found. Please check the packages table in your database.")
            return

        # A selected package opens a dedicated details view instead of silently doing nothing.
        detail_id = st.session_state.get("detail_package_id")
        if detail_id is not None:
            selected = next((p for p in packages if str(p["id"]) == str(detail_id)), None)
            if selected is None:
                st.session_state.pop("detail_package_id", None)
            else:
                st.button("← Back to all packages", key="back_to_packages", on_click=back_to_packages)
                st.markdown(f"# {selected['title']}")
                st.caption(f"📍 {selected['destination']}  ·  🗓️ {selected['duration_days']} days")
                images = get_package_images(selected["destination"])
                if images:
                    st.image(images, use_container_width=True)
                else:
                    st.info(f"Photos will appear here when added to images/{destination_image_folder(selected['destination'])}/")
                left, right = st.columns([2, 1])
                with left:
                    st.markdown("### About this tour")
                    st.write(selected["description"] or "Explore this destination with SafarSathi.")
                    st.markdown("### Package includes")
                    st.write("• Tour package details and destination information")
                    st.write("• Travel planning support from SafarSathi")
                    st.caption("Exact hotel, transport and meal inclusions should be confirmed with the travel team before booking.")
                with right:
                    st.markdown("### Package price")
                    st.markdown(f'<div class="price">₹{selected["price"]:,}</div><div class="small-muted">per person</div>', unsafe_allow_html=True)
                    st.write(f"**Duration:** {selected['duration_days']} days")
                    if st.button("Book this tour →", key=f"detail_book_{selected['id']}", use_container_width=True):
                        if st.session_state.user is None:
                            st.session_state.page = "Login"
                            st.info("Please log in to book this tour.")
                        else:
                            st.session_state["prefill_package_id"] = selected["id"]
                            st.session_state.page = "Book a Tour"
                        st.rerun()
                return

        st.markdown("## 🧳 Our Tour Packages")
        st.markdown("Explore the photos, destination, duration and price of each experience.")
        cols = st.columns(3)
        for index, package in enumerate(packages):
            with cols[index % 3]:
                with st.container(border=True):
                    images = get_package_images(package["destination"])
                    if images:
                        st.image(images[0], use_container_width=True)
                        if len(images) > 1:
                            st.caption(f"📸 {len(images)} of 5 photos")
                            mini_cols = st.columns(4)
                            for j, img in enumerate(images[1:5]):
                                with mini_cols[j]:
                                    st.image(img, use_container_width=True)
                        if len(images) < 5:
                            st.caption(f"Add {5-len(images)} more photo(s) in images/{destination_image_folder(package['destination'])}/")
                    else:
                        st.markdown("<div style='background:linear-gradient(135deg,#d7efff,#8bc8ee);border-radius:12px;padding:40px 8px;text-align:center;font-size:2.8rem'>🏞️</div>", unsafe_allow_html=True)
                        st.caption(f"Add photos to images/{destination_image_folder(package['destination'])}/")
                    st.markdown(f"### {package['title']}")
                    st.caption(f"📍 {package['destination']}")
                    st.write(f"🗓️ {package['duration_days']} days")
                    st.write(package["description"] or "Explore this tour.")
                    st.markdown(f'<div class="price">₹{package["price"]:,}</div><div class="small-muted">per person</div>', unsafe_allow_html=True)
                    st.button("View Details →", key=f"package_details_{package['id']}", use_container_width=True, on_click=open_package_details, args=(package["id"],))
    except mysql.connector.Error as error:
        st.error(f"Could not load packages: {error}")


# ---------------- BOOKING SCHEMA CHECK ----------------

def ensure_travel_time_column():
    """Add the optional time column to older databases without deleting data."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM bookings LIKE 'travel_time'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE bookings ADD COLUMN travel_time TIME NULL AFTER travel_date")
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


# ---------------- BOOK A TOUR ----------------

def show_booking():
    st.header("📅 Book a Tour")
    st.write("Choose your package, travel date, preferred start time and traveller count below.")
    st.info("Travel date and time are required. Past date/time selections will be rejected. Your request is saved as Pending until the travel team approves it.")

    try:
        ensure_travel_time_column()
        packages = get_packages()
    except mysql.connector.Error as error:
        st.error(f"Could not load packages: {error}")
        st.info("If this mentions permissions, run the ALTER TABLE statement from schema.sql once in MySQL Workbench.")
        return

    if not packages:
        st.warning("No active tour packages are available.")
        return

    # Map package IDs to readable labels.
    # The selected value is always the actual database package ID.
    package_labels = {
        package["id"]: (
            f"{package['title']} — "
            f"₹{package['price']} per person "
            f"({package['duration_days']} days)"
        )
        for package in packages
    }

    with st.form("booking_form"):
        package_ids = list(package_labels.keys())
        preferred_id = st.session_state.get("prefill_package_id")
        default_index = package_ids.index(preferred_id) if preferred_id in package_ids else 0
        selected_package_id = st.selectbox(
            "Select Tour Package",
            options=package_ids,
            index=default_index,
            format_func=lambda package_id: package_labels[package_id],
            key="booking_package_select",
        )

        travel_date = st.date_input(
            "Travel Date",
            value=date.today(),
            min_value=date.today(),
            help="Choose today or a future date. If choosing today, select a time later than the current time.",
            key="booking_travel_date",
        )
        travel_time = st.time_input(
            "Preferred Reporting / Start Time",
            value=time(9, 0),
            help="Choose a preferred start time. If the travel date is today, this time must still be in the future. Final timing is confirmed by SafarSathi.",
            key="booking_travel_time",
        )

        travellers = st.number_input(
            "Number of Travellers",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
        )

        hotel_preference = st.selectbox(
            "Hotel Preference",
            options=["Standard", "Deluxe", "Premium"],
        )

        estimated_total = next((p["price"] for p in packages if p["id"] == selected_package_id), 0) * int(travellers)
        st.markdown(f"**Estimated package total: ₹{estimated_total:,.2f}**")
        st.caption("Booking is a request only. No payment is taken on this screen.")
        submitted = st.form_submit_button(
            "Check Date & Time and Submit Booking",
            use_container_width=True,
        )

    if submitted:
        user = st.session_state.user

        if not user:
            st.error("Please log in before booking.")
            return

        try:
            selected_datetime = datetime.combine(travel_date, travel_time)
            if selected_datetime <= datetime.now():
                st.error("Please choose a future date and time. The selected travel time has already passed.")
                return

            # Confirm the selected package is still active.
            valid_package = fetch_all(
                """
                SELECT id
                FROM packages
                WHERE id = %s AND active = TRUE
                LIMIT 1
                """,
                (selected_package_id,),
            )

            if not valid_package:
                st.error(
                    "This package is no longer available. "
                    "Please select another package."
                )
                return

            execute_query(
                """
                INSERT INTO bookings
                    (user_id, package_id, travel_date, travel_time, travellers,
                     hotel_preference, status, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pending', 'Not Paid')
                """,
                (
                    user["id"],
                    selected_package_id,
                    travel_date,
                    travel_time.strftime("%H:%M:%S"),
                    int(travellers),
                    hotel_preference,
                ),
            )

            st.success(
                "Booking request submitted successfully! "
                "Your booking status is Pending."
            )
            st.info(
                "This is a booking request, not a confirmed ticket. "
                "Please wait for the travel team to approve it."
            )

        except mysql.connector.Error as error:
            st.error(f"Booking could not be saved: {error}")


# ---------------- MY BOOKINGS ----------------

def show_my_bookings():
    st.header("My Bookings")

    user = st.session_state.user

    try:
        bookings = fetch_all(
            """
            SELECT
                b.id,
                p.title,
                p.destination,
                p.price,
                b.travel_date,
                b.travel_time,
                b.travellers,
                b.hotel_preference,
                b.status,
                b.payment_status,
                b.created_at
            FROM bookings b
            JOIN packages p ON p.id = b.package_id
            WHERE b.user_id = %s
            ORDER BY b.id DESC
            """,
            (user["id"],),
        )

        if not bookings:
            st.info(
                "You have no bookings yet. "
                "Go to Book a Tour to create your first booking."
            )
            return

        for booking in bookings:
            with st.container(border=True):
                st.subheader(
                    f"Booking #{booking['id']} — {booking['title']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"📍 Destination: {booking['destination']}"
                    )
                    st.write(f"📅 Travel date: {booking['travel_date']}")
                    if booking.get("travel_time"):
                        st.write(f"🕒 Preferred time: {booking['travel_time']}")
                    st.write(f"👥 Travellers: {booking['travellers']}")

                with col2:
                    st.write(
                        f"🏨 Hotel: {booking['hotel_preference']}"
                    )
                    st.write(
                        f"💰 Package price: ₹{booking['price']} per person"
                    )
                    st.write(
                        f"💳 Payment: {booking['payment_status']}"
                    )

                st.write(f"**Booking status:** {booking['status']}")

    except mysql.connector.Error as error:
        st.error(f"Could not load your bookings: {error}")


# ---------------- ADMIN DASHBOARD ----------------

def show_admin():
    st.header("Admin Dashboard")
    st.write("View customer bookings and update their status.")

    try:
        bookings = fetch_all(
            """
            SELECT
                b.id,
                u.name AS customer_name,
                u.email,
                p.title AS package_title,
                b.travel_date,
                b.travel_time,
                b.travellers,
                b.hotel_preference,
                b.status,
                b.payment_status,
                b.created_at
            FROM bookings b
            JOIN users u ON u.id = b.user_id
            JOIN packages p ON p.id = b.package_id
            ORDER BY b.id DESC
            """
        )

        if not bookings:
            st.info("No booking requests have been received yet.")
        else:
            st.dataframe(bookings, use_container_width=True)

            st.divider()
            st.subheader("Update Booking Status")

            booking_ids = [booking["id"] for booking in bookings]

            selected_booking_id = st.selectbox(
                "Select Booking ID",
                options=booking_ids,
                format_func=lambda booking_id: (
                    f"#{booking_id} — "
                    + next(
                        booking["customer_name"]
                        for booking in bookings
                        if booking["id"] == booking_id
                    )
                ),
            )

            current_booking = next(
                booking for booking in bookings
                if booking["id"] == selected_booking_id
            )

            statuses = [
                "Pending",
                "Approved",
                "Rejected",
                "Completed",
            ]

            current_status = current_booking["status"]
            default_index = (
                statuses.index(current_status)
                if current_status in statuses
                else 0
            )

            with st.form("admin_status_form"):
                new_status = st.selectbox(
                    "New Status",
                    options=statuses,
                    index=default_index,
                )

                update_clicked = st.form_submit_button(
                    "Update Status",
                    use_container_width=True,
                )

            if update_clicked:
                execute_query(
                    """
                    UPDATE bookings
                    SET status = %s
                    WHERE id = %s
                    """,
                    (new_status, selected_booking_id),
                )

                st.success("Booking status updated.")
                st.rerun()

    except mysql.connector.Error as error:
        st.error(f"Admin dashboard error: {error}")


# ---------------- NAVIGATION ----------------

if st.session_state.user is None:
    st.sidebar.title("Navigation")

    public_pages = ["Home", "Tour Packages", "Login", "Register"]
    if st.session_state.page not in public_pages:
        st.session_state.page = "Home"
    public_page = st.sidebar.radio(
        "Choose a page",
        public_pages,
        index=public_pages.index(st.session_state.page),
        key="public_navigation",
    )
    st.session_state.page = public_page

    if public_page == "Home":
        show_home()
    elif public_page == "Tour Packages":
        show_packages()
    elif public_page == "Login":
        show_login()
    elif public_page == "Register":
        show_register()

else:
    user = st.session_state.user

    st.sidebar.title("Navigation")
    st.sidebar.success(f"Logged in: {user['name']}")
    st.sidebar.caption(user["email"])

    pages = [
        "Home",
        "Tour Packages",
        "Book a Tour",
        "My Bookings",
    ]

    if user["role"] == "admin":
        pages.append("Admin Dashboard")

    if st.session_state.page not in pages:
        st.session_state.page = "Home"
    selected_page = st.sidebar.radio(
        "Choose a page",
        pages,
        index=pages.index(st.session_state.page),
        key="logged_in_navigation",
    )
    st.session_state.page = selected_page

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = "Home"
        st.rerun()

    if selected_page == "Home":
        show_home()
    elif selected_page == "Tour Packages":
        show_packages()
    elif selected_page == "Book a Tour":
        show_booking()
    elif selected_page == "My Bookings":
        show_my_bookings()
    elif selected_page == "Admin Dashboard":
        if user["role"] == "admin":
            show_admin()
        else:
            st.error("You do not have admin access.")


# ---------------- FOOTER (render after the selected page) ----------------
st.markdown("<hr style='border:0;border-top:1px solid #d9ecfa;margin:36px 0 12px'>", unsafe_allow_html=True)
st.markdown("<div style='background:#104d82;color:white;border-radius:16px;padding:18px 22px;text-align:center'>✈️ <b>SafarSathi Tours & Travels</b> &nbsp; · &nbsp; Better Places. Bigger Dreams. <div style='font-size:.8rem;opacity:.85;margin-top:5px'>© 2026 SafarSathi. Plan your next journey with us.</div></div>", unsafe_allow_html=True)
