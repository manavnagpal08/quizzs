import streamlit as st
import json
import random
from google.cloud.firestore import Client, DocumentSnapshot # Placeholder imports for type hinting

# --- 0. Simulated Dependencies (Sentiment Analysis) ---
# In a real app, you would load your joblib model and vectorizer here.
# Since we cannot load joblib or scikit-learn in this environment, we simulate the prediction
# using simple keyword analysis.

def predict_sentiment(review_text: str):
    """
    Simulates a sentiment analysis model prediction.
    In a real application, this would load a pre-trained model and vectorizer.
    """
    if not review_text:
        return "neutral", "😐"

    text = review_text.lower()
    positive_keywords = ["great", "excellent", "love", "amazing", "fantastic", "best", "perfect", "awesome", "happy", "wonderful"]
    negative_keywords = ["bad", "terrible", "disappointing", "worst", "awful", "horrible", "poor", "unusable", "unhappy", "broke"]

    pos_count = sum(text.count(word) for word in positive_keywords)
    neg_count = sum(text.count(word) for word in negative_keywords)

    # Simple scoring logic
    if pos_count > neg_count + 1:
        return "positive", "😊"
    elif neg_count > pos_count + 1:
        return "negative", "😞"
    else:
        return "neutral", "😐"

# --- 1. Firebase Initialization and Utilities ---

# Global variables provided by the environment (MUST be used)
APP_ID = None
FIREBASE_CONFIG = None
AUTH_TOKEN = None

# Check for global environment variables
try:
    APP_ID = str(__app_id)
except NameError:
    APP_ID = 'default-ecommerce-app'
    st.sidebar.warning("Using default App ID.")

try:
    FIREBASE_CONFIG = json.loads(__firebase_config)
except (NameError, json.JSONDecodeError):
    FIREBASE_CONFIG = {}
    st.error("Firebase config not found. Data persistence is disabled.")

try:
    AUTH_TOKEN = str(__initial_auth_token)
except NameError:
    AUTH_TOKEN = None

# Initialize Firebase services only once
@st.cache_resource
def initialize_firebase():
    """Initializes Firebase App, Auth, and Firestore."""
    if not FIREBASE_CONFIG:
        return None, None, None

    try:
        from firebase_admin import initialize_app, credentials
        from firebase_admin import auth as f_auth
        from firebase_admin import firestore
        import google.auth
        import google.auth.transport.requests

        # Check if the app is already initialized
        if not initialize_app: # Simple check to bypass re-initialization logic
            return None, None, None

        # Use a dummy credential for initialization in environments that require it
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": FIREBASE_CONFIG.get("projectId", "demo-project"),
            "private_key_id": "dummy-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMQIDAQQFAAS...",
            "client_email": "dummy-client@demo-project.iam.gserviceaccount.com",
            "client_id": "dummy-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
            "universe_domain": "googleapis.com"
        })
        
        # We try to mimic the canvas environment's authentication pattern
        # by initializing the SDKs and preparing for auth.
        
        # Note: Since the provided environment only gives the config/token but not the full
        # client libraries like getAuth/getFirestore, we rely on the backend environment's
        # pre-configured access using google-cloud-firestore if available.
        
        # For simplicity and to comply with the single-file requirement, we'll use
        # google.cloud.firestore Client directly, which often works in these environments.
        
        db = firestore.client()
        
        # Simulate user ID retrieval based on environment provided token
        user_id = "anonymous_" + str(random.randint(1000, 9999))
        if AUTH_TOKEN:
            try:
                # This part is highly environment-dependent. In a typical client-side JS environment,
                # you'd use signInWithCustomToken. Here, we must simulate finding a user ID.
                # Since we can't run the client-side SDK, we rely on a dummy user ID.
                user_id = "auth_" + AUTH_TOKEN[:8] 
            except Exception:
                pass # Use dummy ID if token check fails

        st.session_state['user_id'] = user_id
        return db, user_id
    
    except Exception as e:
        st.error(f"Could not initialize Firebase/Firestore Client. Error: {e}")
        return None, None

db, USER_ID = initialize_firebase()
PRODUCTS_COLLECTION = f"artifacts/{APP_ID}/public/data/products"

def add_product(name, price, description, image_url):
    """Adds a new product document to Firestore."""
    if db is None:
        st.error("Database not initialized.")
        return False
    try:
        product_data = {
            "name": name,
            "price": float(price),
            "description": description,
            "image_url": image_url,
            "created_by": USER_ID,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        db.collection(PRODUCTS_COLLECTION).add(product_data)
        return True
    except Exception as e:
        st.error(f"Error adding product: {e}")
        return False

def get_all_products():
    """Fetches all products and their nested reviews."""
    if db is None:
        return []
    
    products_list = []
    try:
        products_ref = db.collection(PRODUCTS_COLLECTION).stream()
        
        for product_doc in products_ref:
            product_id = product_doc.id
            product_data = product_doc.to_dict()
            product_data['id'] = product_id
            
            # Fetch reviews subcollection for this product
            reviews_ref = db.collection(PRODUCTS_COLLECTION).document(product_id).collection('reviews').stream()
            product_data['reviews'] = [review.to_dict() for review in reviews_ref]
            
            products_list.append(product_data)
            
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []
        
    return products_list

def add_review(product_id, reviewer_name, review_text):
    """Adds a review to a product's subcollection."""
    if db is None:
        st.error("Database not initialized.")
        return False
    
    try:
        sentiment, emoji = predict_sentiment(review_text)
        
        review_data = {
            "reviewer": reviewer_name,
            "text": review_text,
            "sentiment": sentiment,
            "emoji": emoji,
            "created_by": USER_ID,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        db.collection(PRODUCTS_COLLECTION).document(product_id).collection('reviews').add(review_data)
        return True
    except Exception as e:
        st.error(f"Error adding review: {e}")
        return False

# --- 2. Streamlit Page Components ---

def product_display_page():
    """Renders the main product display and review submission page."""
    st.title("🛍️ E-commerce Product Catalog")
    st.write("Browse products and submit your reviews below.")
    
    # Initialize refresh flag in session state
    if 'refresh_products' not in st.session_state:
        st.session_state.refresh_products = True

    # Use caching and refresh flag to manage data fetching
    if st.session_state.refresh_products:
        with st.spinner("Loading products and reviews..."):
            st.session_state.products = get_all_products()
        st.session_state.refresh_products = False

    products = st.session_state.products
    
    if not products:
        st.info("No products available yet. Go to 'Add Product' to list one!")
        return

    # Sort by creation time (simulated, as firestore.SERVER_TIMESTAMP isn't available for sorting without a field)
    products.sort(key=lambda x: x.get('created_at', 0), reverse=True)

    for product in products:
        product_id = product['id']
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Use st.image for product image
            st.image(
                product.get('image_url', 'https://placehold.co/400x300/60a5fa/ffffff?text=Product'),
                caption=f"Price: ${product['price']:.2f}",
                width=200
            )

        with col2:
            st.subheader(product['name'])
            st.markdown(f"**Price:** <span style='color: #10b981; font-weight: bold;'>${product['price']:.2f}</span>", unsafe_allow_html=True)
            st.write(f"**Description:** {product['description']}")

        st.markdown("---")
        
        # --- Review Display ---
        st.markdown(f"**Past Reviews ({len(product['reviews'])})**")
        if product['reviews']:
            
            # Sort reviews by creation time (newest first)
            product['reviews'].sort(key=lambda x: x.get('created_at', 0), reverse=True)

            for review in product['reviews'][:3]: # Show up to 3 reviews initially
                st.markdown(
                    f"<div style='background-color: #f3f4f6; padding: 10px; border-radius: 8px; margin-bottom: 5px;'>"
                    f"**{review['reviewer']}** {review['emoji']} <span style='font-size: 0.9em;'>({review['sentiment']})</span>"
                    f"<p style='margin-top: 5px; margin-bottom: 0;'>{review['text']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            if len(product['reviews']) > 3:
                 st.caption(f"and {len(product['reviews']) - 3} more reviews...")
        else:
            st.info("Be the first to leave a review!")

        # --- Review Submission Form ---
        with st.expander(f"Submit a Review for {product['name']}", expanded=False):
            with st.form(key=f'review_form_{product_id}'):
                reviewer_name = st.text_input("Your Name", key=f'name_{product_id}', value="Anonymous")
                review_text = st.text_area("Your Review", key=f'text_{product_id}')
                
                # Predict sentiment on button click
                submitted = st.form_submit_button("Submit Review")

                if submitted:
                    if review_text.strip():
                        if add_review(product_id, reviewer_name, review_text):
                            st.success("Review submitted successfully! Refreshing product list...")
                            # CRITICAL: Set the flag to true to force a re-fetch and refresh the page
                            st.session_state.refresh_products = True
                            st.experimental_rerun()
                        else:
                            st.error("Failed to submit review.")
                    else:
                        st.warning("Please write a review before submitting.")

        st.markdown("---") # End of product section

def add_product_page():
    """Renders the Admin Panel for adding new products."""
    st.title("➕ Admin Panel: Add New Product")
    st.markdown("Use this panel to quickly list a new item in the catalog.")

    if db is None:
        st.error("Cannot add products: Database is not connected.")
        return

    with st.form("add_product_form", clear_on_submit=True):
        name = st.text_input("Product Name", max_chars=100)
        price_str = st.text_input("Price (e.g., 49.99)", max_chars=10)
        description = st.text_area("Product Description", max_chars=500)
        image_url = st.text_input(
            "Image URL",
            placeholder="e.g., https://placehold.co/400x300",
            value="https://placehold.co/400x300/4f46e5/ffffff?text=New+Product"
        )
        
        submitted = st.form_submit_button("Add Product to Catalog 🚀")
        
        if submitted:
            try:
                price = float(price_str)
                if not name or not description or price <= 0:
                    st.error("Please fill in all fields correctly (Name, Description, Price > 0).")
                else:
                    if add_product(name, price, description, image_url):
                        st.success(f"Product '{name}' added successfully! Check the Products page.")
                        # Optionally set refresh flag for product page
                        st.session_state.refresh_products = True
                    else:
                        st.error("Failed to add product to Firestore.")
            except ValueError:
                st.error("Invalid price format. Please enter a valid number.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


# --- 3. Main Streamlit App Navigation ---

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(
        page_title="E-commerce Platform", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Products", "Add Product"])
    
    # Display user info for context
    if USER_ID:
        st.sidebar.markdown(f"**Logged in as:** `{USER_ID}`")
    
    if page == "Products":
        product_display_page()
    elif page == "Add Product":
        add_product_page()

if __name__ == "__main__":
    main()
