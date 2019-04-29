#pragma once

#include "SFML/Graphics.hpp"
#include "Player.h"

/// The various states the launcher can be in.
enum LaunchState
{
	// The state where the player is setting the power of the launch.
	SettingPower,
	// The state where the player is setting the angle of the launch.
	SettingAngle,
	// The state after the player has finished the launch process.
	Finished
};

/// The on screen display for the power and angle the player will
/// be launched at. This also handles the player input for the launcher.
/// It works in 2 phases. First the power is set then the angle is set.
/// Similar to mario golf where the power slider goes up and down and you
/// have to stop it near the top. Then the angle goes side to side/up and down
/// and you have to stop it at the right angle.
class Launcher : public sf::Drawable
{
	public:
		Launcher(const sf::VideoMode& screen_size);

		void Update();
		void MoveToNextState(Player& player);

	private:
		sf::Vector2<float> DetermineLaunchVector();
		virtual void draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const;

		// The current state of the launcher.
		LaunchState State;

		/// The current power setting for the launcher.
		/// This will constantly change during the setting power phase
		/// until the player moves to the setting angle phase.
		float Power;

		/// The current angle setting for the launcher in degrees.
		/// 0 degrees is straight up and 90 degrees is straight right.
		float AngleInDegrees;

		sf::RectangleShape PowerMeter;
		sf::RectangleShape AngleMeter;
		unsigned int ScreenWidth;
		unsigned int ScreenHeight;
};