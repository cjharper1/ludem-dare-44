#include "SFML/Graphics.hpp"
#include "SFML/System.hpp"
#include "Launcher.h"
#include "Player.h"
#include "StageHazard.h"
#include "WorldMap.h"

int main()
{
    // CREATE THE MAIN GAME WINDOW.
	sf::VideoMode window_size(1280, 720);
    sf::RenderWindow window(window_size, "Example Game");

    // CREATE THE PLAYER.
	// Position the player starting on the bottom left of the screen.
	// Some padding is applied so the launcher does not cover the player.
	constexpr unsigned int PADDING = 30;
	sf::Vector2<float> player_initial_position(PADDING, window_size.height - PADDING);
	Player player(player_initial_position, window_size);

	// CREATE THE STAGE HAZARDS.
	const float middle_of_screen_y_value = window_size.height / 2;
	const float middle_of_screen_x_value = window_size.width / 2;
	const sf::Vector2<float> middle_of_screen(middle_of_screen_x_value, middle_of_screen_y_value);
	std::vector<StageHazard> stage_hazards;
	stage_hazards.emplace_back(HazardType::Cactus, middle_of_screen);

	// CREATE THE LAUNCHER.
	Launcher launcher(window_size);

    // CREATE THE WORLD MAP.
	WorldMap world_map(player, stage_hazards, launcher);

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

			// CHECK IF THE USER PRESSED ESCAPE.
			// This is an alternative way to end the game.
			if (current_event.type == sf::Event::KeyPressed && current_event.key.code == sf::Keyboard::Escape)
			{
				window.close();
				break;
			}

			// HANDLE USER INPUT.
			world_map.HandleUserInput(current_event);
        }

		// UPDATE THE WORLD MAP.
		world_map.Update();

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