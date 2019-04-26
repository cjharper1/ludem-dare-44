#pragma once

#include <thread>
#include <memory>
#include <SFML/Graphics.hpp>
#include "EventHandler/EventHandler.h"

class PhysicsEngine
{
    public:
        explicit PhysicsEngine(
            const EventHandler& event_handler,
            sf::RenderWindow& render_window);

        void Process(sf::Shape& shape);
    private:

        sf::RenderWindow& MainRenderWindow;
        EventHandler CharacterActionsEventHandler;
};