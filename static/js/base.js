$('.top').click(function(){
    document.documentElement.scrollTop = 0;
});

$('.cart-popup').hide();
$('.login-popup').hide();

$('.input-label').hide();

// Function to fetch cart data via AJAX
var csrftoken = getCookie('csrftoken'); 

// Function to get CSRF token from cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var timeout;

$('#loggined-user').hover(function(){
    clearTimeout(timeout); // Clear any previous timeout
    $('.user-options').show();
}, function(){
    // Set a timeout to hide user options after 500 milliseconds
    timeout = setTimeout(function(){
        $('.user-options').hide();
    }, 500);
});

$('.user-options').hover(function(){
    clearTimeout(timeout); // Clear the timeout if user options are hovered
}, function(){
    // Set a timeout to hide user options after 500 milliseconds
    timeout = setTimeout(function(){
        $('.user-options').hide();
    }, 500);
});

// Handle form submission
$('.checkout-form').submit(function(event) {
    // Prevent the default form submission
    event.preventDefault();
    const billingName = $('input[name="name"]').val();
    const billingAddress = $('textarea[name="address"]').val();
    const billingEmail = $('input[name="email"]').val();
    const billingCity = $('input[name="city"]').val();
    const billingPostalCode = $('input[name="postal_code"]').val();
    const billingCountry = $('input[name="country"]').val();
    const selectedPaymentMethod = $('input[name="payment_method"]:checked').val();
    const totalAmount = parseInt($('#total_price').data('total-price'));
    
    // products from cart.
    var cartItems = [] 
    $('.cart-item').each(function(){
        var productId = $(this).data("product-id");
        var quantity = $(this).data("quantity");
        if(productId){
            cartItems.push({
                'product_id': productId,
                'quantity': quantity,
            });
        }
    });

    // Data to place order.
    const data = {
        'name' : billingName,
        'address' : billingAddress,
        'email' : billingEmail,
        'city' : billingCity,
        'postal_code' : billingPostalCode,
        'country' : billingCountry,
        'payment_method' : selectedPaymentMethod,
        'total_amount' : totalAmount,
        'cart_items': JSON.stringify(cartItems),
    }

    // Example: Send the selected value in an AJAX request
    $.ajax({
        url: '{% url "shop:save-order" %}',
        type: 'POST',
        data: data,
        headers: {
            'X-CSRFToken': csrftoken,
        },
        success: function(response) {
            // Handle success response
        },
        error: function(xhr, status, error) {
            // Handle error response
        }
    });
});

// Show label when input field gains focus
$('input, textarea').focus(function() {
    $(this).prev('.input-label').fadeIn();
});

// Hide label when input field loses focus if no value entered
$('input, textarea').blur(function() {
    if ($(this).val() === '') {
        $(this).prev('.input-label').fadeOut();
    }
});

// Check for initial values and show labels accordingly
$('input, textarea').each(function() {
    if ($(this).val() !== '') {
        $(this).prev('.input-label').show();
    }
});
const breadcrumbs = $('.breadcrumbs');
const homeLogo = $('.home-logo');

// Calculate the initial width of the breadcrumbs container
const initialWidth = breadcrumbs.width();

// Calculate the width of the home logo
const homeLogoWidth = homeLogo.width();

// Decrease the width of the breadcrumbs container gradually until only the home logo is visible
let currentWidth = initialWidth;
const intervalId = setInterval(function() {
    currentWidth -= 1; // Decrease width by 10 pixels (adjust as needed)
    breadcrumbs.width(currentWidth);
    
    // Stop decreasing width when only the home logo is visible
    if (currentWidth <= homeLogoWidth) {
        clearInterval(intervalId);
    }
}, 1); // Adjust the interval time as needed

// When hovered, expand the breadcrumbs container back to its original width
breadcrumbs.mouseenter(function() {
    breadcrumbs.width(initialWidth);
});

// When not hovered, set the width back to only show the home logo
breadcrumbs.mouseleave(function() {
    breadcrumbs.width(homeLogoWidth);
});

// Update cart popup.
function updateCartItems(cartItems) {
    var cartItemsContainer = $('.cart_items tbody');
    cartItemsContainer.empty(); // Clear existing cart items
    
    // Show or hide the "No items in cart" message based on cart items existence
    if (cartItems.length === 0) {
        $('.cart-popup').find('.cart_items').append($('<span>').text('No items in cart'));
    } else {
        $('.cart-popup').find('.cart_items span').remove(); // Remove the message if cart is not empty
    }

    // Loop through the received cart items and append them to the table body
    cartItems.forEach(function(item) {
        var row = $('<tr>').addClass('cart-item');
        // Append table data for each cart item
        row.append($('<td>').append($('<img>').attr('src', item.image)));
        row.append($('<td>').addClass('product-name').append($('<span>')).text(item.product_name));
        row.append($('<td>').append($('<span>')).text(item.quantity));
        row.append($('<td>').append($('<span>').addClass('price').text('₹' + item.sub_total)));
        row.append($('<td>').append($('<img>').addClass('delete').attr('src', '{% static "images/trash.png" %}').attr('title', 'Remove item from cart').attr('onclick', "deleteItemFromCart('"+item.id+"')")));
        // Append the row to the table body
        cartItemsContainer.append(row);
    });
}

// Handle decrease item from cart.
function decreaseItemFromCart(productId){
    $.ajax({
        type: 'POST',
        url: '{% url "shop:decrease-item-from-cart" %}',
        data: {
            'product_id': productId,
        },
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Assuming you have a function getCookie() defined
        },
        dataType: 'json',
        success: (res)=>{
            if(res){
                var message = $('<div>');
                message.addClass('message');
                if(res.success){
                    message.addClass('success');
                }else {
                    message.addClass('warning');
                }
                message.text(res.message);
                $('.messages').empty();
                $('.messages').append(message);
                $('.messages').show();
                updateCartItems(res.cart_items);
                $('.count').text(res.cart_items_count);
                $('.checkout-button .price').text('₹' + res.total_price.toLocaleString());
                $('#total_price').text('₹' + res.total_price.toLocaleString());

                // Hide the message after 5 seconds (adjust as needed)
                setTimeout(() => {
                    message.remove();
                }, 1000);
            }
        },
        error: (err)=>{
            console.log(err);
        }
    });
}

// Handle add to cart click.
function handleAddToCart(productId){
    $.ajax({
        type: 'POST',
        url: '',//{% url "shop:add-to-cart" %}
        data: {
            'product_id': productId,
        },
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Assuming you have a function getCookie() defined
        },
        dataType: 'json',
        success: (res)=>{
            if(res){
                var message = $('<div>');
                message.addClass('message');
                if(res.success){
                    message.addClass('success');
                }else {
                    message.addClass('warning');
                }
                message.text(res.message);
                $('.messages').empty();
                $('.messages').append(message);
                $('.messages').show();
                updateCartItems(res.cart_items);
                $('.count').text(res.cart_items_count);
                $('.checkout-button .price').text('₹' + res.total_price.toLocaleString());
                $('#total_price').text('₹' + res.total_price.toLocaleString());

                // Hide the message after 5 seconds (adjust as needed)
                setTimeout(() => {
                    message.remove();
                }, 1000);
            }
        },
        error: (err)=>{
            console.log(err);
        }
    });
}

// Handle add to wishlist click.
function handleAddToWishlist(productId){
    if(isLoggedIn=='True'){
        $.ajax({
            type: 'POST',
            url: '{% url "shop:add-to-wishlist" %}',
            data: {
                'product_id': productId,
                'name':'name',
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Assuming you have a function getCookie() defined
            },
            dataType: 'json',
            success: (res)=>{
                if(res){
                    var message = $('<div>');
                    message.addClass('message');
                    if(res.success){
                        message.addClass('success');
                    }else {
                        message.addClass('warning');
                    }
                    message.text(res.message);
                    $('.messages').empty();
                    $('.messages').append(message);
                    $('.messages').show();

                    // Hide the message after 5 seconds (adjust as needed)
                    setTimeout(() => {
                        message.remove();
                    }, 3000);
                }
            },
            error: (err)=>{
                console.log(err);
            }
        });
    } else {
        $('.login-popup').toggle();
        $('.login-popup').css('display', 'flex');
    }
}
var isLoggedIn = '{{request.user.is_authenticated}}';

$(document).ready(function() {
    $('#loading-screen').hide();
});

// delete item from cart.
function deleteItemFromCart(cart_item_id){
    var url = '/delete-item-from-cart/'+cart_item_id;
    $.ajax({
        url: url,
        type: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        success: (res)=>{
            if(res){
                var message = $('<div>');
                message.addClass('message');
                if(res.success){
                    message.addClass('success');
                }else {
                    message.addClass('warning');
                }
                message.text(res.message);
                $('.messages').empty();
                $('.messages').append(message);
                $('.messages').show();
                $('.count').text(res.cart_items_count);
                $('.checkout-button .price').text('₹' + res.total_price.toLocaleString());
                updateCartItems(res.cart_items);
                // Hide the message after 5 seconds (adjust as needed)
                setTimeout(() => {
                    message.remove();
                }, 1000);
            }
        },
        error: (err)=>{
            console.log(err);
        },
    })
}

$('.wishlist-icon').click((event)=>{
    if(isLoggedIn=='True'){
        window.location.href = "{% url 'shop:wishlist' %}";
    }else{
        $('.login-popup').toggle();
        $('.login-popup').css('display', 'flex');
        event.stopPropagation();
    }
});

// Toggle cart popup
$('.cart').click((event) => {
    $('.cart-popup').toggle();
    // Prevent the event from propagating further
    event.stopPropagation();
});
$(document).click((event)=>{
    if(!$(event.target).closest('.cart-popup', '.cart').length) {
        $('.cart-popup').hide();
    }
    if(!$(event.target).closest('.login-popup', 'wishlist-icon').length) {
        // $('.login-popup').hide();
    }else if($(event.target).is('.close-login-popup') || $(event.target).is('.cancel-login-popup') ||  $(event.target).not('.add-to-wishlist')){
        $('.login-popup').hide();
    }

    // Add to cart.
    $('#addToCart').click(function() {
        var cartProductId = $(this).attr('data-product-id');

        // Your logic here to handle the product ID and perform AJAX request
        $('#loading-screen').show();
        $.ajax({
            url: '/add-to-cart/' + cartProductId,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Assuming you have a function getCookie() defined
            },
            success: function(data) {
                $('#loading-screen').hide();

                // Append the received message to the messages div
                var messageDiv = $('<div class="message success"></div>').text(response);
                $('.messages').append(messageDiv);
            }
        });
    });
});