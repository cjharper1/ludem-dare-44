#pragma once

#include <SFML/Graphics.hpp>

class EventHandler
{
    public:
        explicit EventHandler() = default;
        void HandleEvent(
            const sf::Event& current_event,
            sf::RenderWindow& window,
            sf::Shape& shape);
        
    private:
        void EventHandler::HandleMouseEvent(
            const sf::Event& current_event,
            sf::Shape& shape);
        void ResizeWindow(
            const sf::Event& current_event,
            sf::RenderWindow& window);
        void HandleKeyboardInput(sf::Shape& shape);
            
};