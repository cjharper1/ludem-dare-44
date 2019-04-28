#include "SFML/Graphics.hpp"
#include "SFML/System.hpp"
#include "Player.h"
#include "StageHazard.h"
#include "WorldMap.h"

int main()
{
    // CREATE THE MAIN GAME WINDOW.
    sf::VideoMode desktop_resolution = sf::VideoMode::getDesktopMode();
    sf::RenderWindow window(desktop_resolution, "Example Game");

    // CREATE THE PLAYER.
	Player player;

	// CREATE THE STAGE HAZARDS.
	const float middle_of_screen_y_value = desktop_resolution.height / 2;
	const float middle_of_screen_x_value = desktop_resolution.width / 2;
	const sf::Vector2<float> middle_of_screen(middle_of_screen_x_value, middle_of_screen_y_value);
	std::vector<StageHazard> stage_hazards;
	stage_hazards.emplace_back(HazardType::Cactus, middle_of_screen);

    // CREATE THE WORLD MAP.
	WorldMap world_map(player, stage_hazards);

    // EXECUTE GAME AS LONG AS WINDOW IS OPEN.
    while (window.isOpen())
    {
        // CONSUME EACH EVENT PRODUCED BY PLAYER INPUT.
        sf::Event current_event;
        while (window.pollEvent(current_event))
        {
            // CHECK IF THE USER CLOSED THE WINDOW.
            if (current_event.type == sf::Event::Closed)
            {
                window.close();
                break;
            }

			// HANDLE USER INPUT.
			world_map.HandleUserInput(current_event);
        }

		// HANDLE ANY COLLISIONS THAT MAY HAVE OCCURRED.
		world_map.HandleCollisions();

        // CLEAR THE WINDOW BUFFER.
        window.clear();

        // DRAW THE WORLD MAP.
        window.draw(world_map);

        // DISPLAY THE NEW SCREEN.
        window.display();

		// Limit game to 60 fps.
		sf::Time time_to_render_one_frame = sf::milliseconds(16);
		sf::sleep(time_to_render_one_frame);
    }

    return 0;
}