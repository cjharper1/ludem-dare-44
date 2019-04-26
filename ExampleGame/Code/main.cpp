#include <optional>
#include "SFML/Graphics.hpp"
#include "SFML/System.hpp"
#include "Box2D/Box2D.h"

int main()
{
    // CREATE THE MAIN WINDOW.
    sf::RenderWindow window(
        sf::VideoMode(1000, 1000),
        "Example Game",
        sf::Style::Default);

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
            if (current_event.type == sf::Event::Closed)
            {
                window.close();
                break;
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