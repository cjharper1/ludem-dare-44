#include "EventHandler.h"

void EventHandler::HandleEvent(
    const sf::Event& current_event,
    sf::RenderWindow& window,
    sf::Shape& shape)
{
    // DETERMINE THE TYPE OF EVENT.
    switch(current_event.type)
    {
        case (sf::Event::MouseButtonPressed):
        {
            HandleMouseEvent(current_event, shape);
            break;
        }
        case (sf::Event::Resized):
        {
            ResizeWindow(current_event, window);
            break;
        }
        case (sf::Event::Closed):
        {
            // CLOSE THE WINDOW.
            window.close();
            break;
        }
        default:
        {
            return;
        }
    }
    
    // HANDLE ANY KEYBOARD ACTIONS.
    // Keyboard actions should not be handled the same as other events
    // because the user could hold down a key.
    HandleKeyboardInput(shape);
}

void EventHandler::HandleMouseEvent(
    const sf::Event& current_event,
    sf::Shape& shape)
{
    // DETERMINE IF THE LEFT MOUSE BUTTON WAS CLICKED.
    bool left_mouse_button_clicked = (current_event.mouseButton.button == sf::Mouse::Left);
    if (left_mouse_button_clicked)
    {
        // CHAGE THE SHAPE COLOR.
        sf::Color current_fill_color = shape.getFillColor();
        bool shape_is_red = (current_fill_color == sf::Color::Red);
        bool shape_is_green = (current_fill_color == sf::Color::Green);
        if (shape_is_red)
        {
            // Change the circle to green.
            shape.setFillColor(sf::Color::Green);
        }
        if (shape_is_green)
        {
            // Change the circle to red.
            shape.setFillColor(sf::Color::Red);
        }
    }
}

void EventHandler::ResizeWindow(
    const sf::Event& current_event,
    sf::RenderWindow& window)
{
    // RESIZE THE WINDOW DISPLAY.
    sf::Vector2u new_window_size(current_event.size.width, current_event.size.height);
    window.setSize(new_window_size);
}

void EventHandler::HandleKeyboardInput(sf::Shape& shape)
{
    // GET USER KEYBOARD INPUT.
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::W))
    {
        shape.move(sf::Vector2f(0, -1));
    }
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::A))
    {
        shape.move(sf::Vector2f(-1, 0));
    }
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::S))
    {
        shape.move(sf::Vector2f(0, 1));
    }
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::D))
    {
        shape.move(sf::Vector2f(1, 0));
    }
}