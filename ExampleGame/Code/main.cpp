#include <optional>
#include "SFML/Graphics.hpp"
#include "SFML/System.hpp"
#include "Box2D/Box2D.h"

int main()
{
    // CREATE THE MAIN WINDOW.
    sf::VideoMode desktop_resolution = sf::VideoMode::getDesktopMode();
    sf::RenderWindow window(desktop_resolution, "Example Game");

    // CREATE A GREEN SQUARE.
    sf::Vector2<float> player_character_size = sf::Vector2<float>(10, 10);
    sf::RectangleShape player_character(player_character_size);
    player_character.setFillColor(sf::Color::Green);

    // EXECUTE GAME AS LONG AS WINDOW IS OPEN.
    while (window.isOpen())
    {
        sf::Event current_event;
        while (window.pollEvent(current_event))
        {
            // CHECK IF THE USER CLOSED THE WINDOW.
            if (current_event.type == sf::Event::Closed)
            {
                window.close();
                break;
            }
            
            // CHECK IF THE USER PRESSED A KEY.
            if (current_event.type == sf::Event::KeyPressed)
            {
                if (sf::Keyboard::isKeyPressed(sf::Keyboard::W))
                {
                    // Move the character up.
                    player_character.move(0, -1);
                }
                if (sf::Keyboard::isKeyPressed(sf::Keyboard::A))
                {
                    // Move the character left.
                    player_character.move(-1, 0);
                }
                if (sf::Keyboard::isKeyPressed(sf::Keyboard::S))
                {
                    // Move the character down.
                    player_character.move(0, 1);
                }
                // HANDLE THE KEY PRESS.
                if (sf::Keyboard::isKeyPressed(sf::Keyboard::D))
                {
                    // Move the character to the right.
                    player_character.move(1, 0);
                }
            }
        }

        // CLEAR THE WINDOW BUFFER.
        window.clear();

        // DRAW THE PLAYER CHARACTER.
        window.draw(player_character);

        // DISPLAY THE NEW SCREEN.
        window.display();
    }

    return 0;
}