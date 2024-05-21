<div align="center">
  <img src="/static/images/logo.png">
  <h1>Kwikmart - An online shopping app</h1>
</div>

## Introduction
Welcome to the My Django Shopping App! This is a simple yet powerful e-commerce platform built using Django framework. This README file will guide you through the installation process and provide an overview of the features and functionalities of this app.

## Features
- **User authentication**: Register, login, and logout functionalities for users.
- **Product management**: Add, edit, and delete products with details like name, description, price, and image.
- **Shopping cart**: Users can add products to their cart, update quantities, and proceed to checkout.
- **Orders**: Users can view their order history and check the status of their orders.
- **Admin panel**: Administrators can manage products, orders, and users through a user-friendly admin interface.

## Installation
1. **Clone the repository:**

```
git clone https://github.com/krishnasankarkk/django-kwikmart.git
```
2. **Navigate to the project directory:**

```
cd django-kwikmart
```
3. **Create a virtual environment for isolate project's dependencies:**

```
python -m venv venv
```
4. **Activate the virtual environment:**

For Windows:
```
venv\Scripts\activate
```

For Linux:
```
source venv/bin/activate
```
5. **Install dependencies:**

```
pip install -r requirements.txt
```
6. **Apply migrations:**

```
python -m manage migrate
```
7. **Create a superuser (admin):**

```
python -m manage createsuperuser
```
8. **Create a .env file by copying .env.example file and filling necessary values:**

```
cp .env.example .env
```
9. **Generate a new secret key and add it to .env file:**

```
python -c 'from django.core.management.utils import get_random_secret_key;print(get_random_secret_key())'
```
Replace the SECRET_KEY value in .env file with the generated key.
10. **Cloudinary Management:**

Cloudinary is used to host images in cloud. Login in to cloudinary to get api settings.
[!Login here]('https://cloudinary.com') and replace these values in .env file:
```
# Cloudinary settings.
CLOUD_NAME = "your_cloud_name"
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
```
11. **Start the development server:**

```
python -m manage runserver
```
12. **Open your web browser and go to `http://localhost:8000` to access the app.**
JQuery is used for DOM Manipulation. Ensure you have a good internet connection to load JQuery API.

## Usage
- Visit the homepage to browse products and add them to your cart.
- Use the navigation menu to explore different sections of the app such as products, cart, and orders.
- Admins can access the admin panel by visiting **`http://localhost:8000/admin`** and login using the superuser credentials created earlier.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:
1. **Fork the repository.**
2. **Create a new branch.**

```
git checkout -b feature-branch
```
4. **Make your changes.**
5. **Commit your changes.**

```
git commit -am 'Add some feature'
```
7. **Push to the branch.**

```
git push origin feature-branch
```
9. **Create a new Pull Request.**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements
- This app was built using the Django web framework.
- Special thanks to the Django community for their support and contributions.
