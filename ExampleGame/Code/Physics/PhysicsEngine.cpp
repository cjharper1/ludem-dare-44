#include <chrono>
#include "PhysicsEngine.h"

PhysicsEngine::PhysicsEngine(
    const EventHandler& event_handler,
    sf::RenderWindow& render_window):
    MainRenderWindow(render_window),
    CharacterActionsEventHandler(event_handler)
{}

void PhysicsEngine::Process(sf::Shape& shape)
{
    // PROCESS PHYSICS AS LONG AS THE GAME IS OPEN.
    while (MainRenderWindow.isOpen())
    {
        // GET EVENTS FROM THE WINDOW.
        sf::Event event;
        while (MainRenderWindow.pollEvent(event))
        {
            // HANDLE THE EVENT.
            CharacterActionsEventHandler.HandleEvent(
                event,
                MainRenderWindow,
                shape);
        }
        
        // ARBITRARILY LIMIT THIS TO PROCESS ONLY 100 TIMES PER SECOND.
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}