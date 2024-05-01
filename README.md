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
3. **Install dependencies:**

```
pip install -r requirements.txt
```
4. **Apply migrations:**

```
python manage.py migrate
```
5. **Create a superuser (admin):**

```
python manage.py createsuperuser
```
6. **Start the development server:**

```
python manage.py runserver
```
7. **Open your web browser and go to `http://localhost:8000`** to access the app.

## Usage
- Visit the homepage to browse products and add them to your cart.
- Use the navigation menu to explore different sections of the app such as products, cart, and orders.
- Admins can access the admin panel by visiting **`http://localhost:8000/admin`** and login using the superuser credentials created earlier.

## License

This project is licensed under the [MIT License](LICENSE).

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

## Acknowledgements
- This app was built using the Django web framework.
- Special thanks to the Django community for their support and contributions.
