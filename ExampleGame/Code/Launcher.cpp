#include <cmath>
#include "Launcher.h"

/// Constructor. The launcher starts in the set power state.
/// \author CJ Harper
/// \date   04/28/2019
Launcher::Launcher(const sf::VideoMode& screen_size):
State(LaunchState::SettingPower),
PowerMeter(),
AngleMeter(),
ScreenWidth(screen_size.width),
ScreenHeight(screen_size.height)
{
    // CREATE THE POWER METER.
	// The power meter will be at the bottom of the screen and extend the full width of the screen.
	// Some padding is added to ensure it does not overflow off the screen.
	// The power meter starts with no width and the width will go up and down to visually indicate the power going up and down.
	// \todo Make this look better and position it better if there is time.
	const unsigned int PADDING = 20;
	PowerMeter.setPosition(sf::Vector2<float>(0, ScreenHeight - PADDING));
	PowerMeter.setSize(sf::Vector2<float>(20, 20));
	PowerMeter.setFillColor(sf::Color::Green);

	// CREATE THE ANGLE METER.
	AngleMeter.setPosition(sf::Vector2<float>(0, ScreenHeight - 5));
	float half_screen_size = (ScreenHeight / 2);
	AngleMeter.setSize(sf::Vector2<float>(half_screen_size, 5));
	AngleMeter.setFillColor(sf::Color::Green);
}

/// Updates the launcher. This should be called every game tick.
/// \author	CJ Harper
/// \date	04/28/2019
void Launcher::Update()
{
	if (State == LaunchState::SettingPower)
	{
		// Check if the power slider is full.
		// This means it should be reset.
		sf::Vector2<float> current_size = PowerMeter.getSize();
		const bool slider_is_full = (current_size.x > ScreenWidth);
		if (slider_is_full)
		{
			// Reset the slider and power level.
			Power = 0;
			current_size.x = 0;
			PowerMeter.setSize(current_size);
			return;
		}

		// Update the power slider.
		// \todo Chopping the screen into sections like this is largely arbitrary. 
		// Maybe we would want to do this in a different way?
		const unsigned int amount_of_pixels_to_grow_per_update = (ScreenWidth / 120);
		current_size.x += amount_of_pixels_to_grow_per_update;
		PowerMeter.setSize(current_size);

		// Update the power level.
		constexpr float MAX_POWER_LEVEL = 8;
		float ratio_of_slider_that_is_full = (current_size.x / ScreenWidth);
		Power = (ratio_of_slider_that_is_full * MAX_POWER_LEVEL);
	}
	else if (State == LaunchState::SettingAngle)
	{
		AngleInDegrees += 1;
		if (AngleInDegrees > 90)
		{
			// Reset the angle.
			AngleInDegrees = 0;
		}

		// Update the sprite.
		// The angle is subtracted from 360 to make the rotation go backwards.
		// Since 360 would be all the way back to the starting position, this is like
		// working backwards from the starting position until it gets to 90 degrees (which is straight up).
		// The reason the rotation needs to be backwards is because the set rotation function goes clockwise. 
		// We want the meter to rotate counter clockwise to match how angles work in an x,y coordinate grid.
		AngleMeter.setRotation(360 - AngleInDegrees);
	}
	else if (State == LaunchState::Finished)
	{
		// There is no need to show the launcher anymore. So the sprites are made invisible.
		// \todo Maybe we want to show this for a few frames before making it disappear
		// to give the player some visual feedback on what their launch result was.
		const sf::Vector2<float> DO_NOT_SHOW(0, 0);
		PowerMeter.setSize(DO_NOT_SHOW);
		AngleMeter.setSize(DO_NOT_SHOW);
	}
}

/// Moves to the next state of the launching process.
/// \author	CJ Harper
/// \date	04/28/2019
void Launcher::MoveToNextState(Player& player)
{
	if (State == LaunchState::SettingPower)
	{
		// Move to setting the angle.
		State = LaunchState::SettingAngle;
	}
	else if (State == LaunchState::SettingAngle)
	{
		// Move to finished.
		State = LaunchState::Finished;

		// Launch the player.
		sf::Vector2<float> launch_vector = DetermineLaunchVector();
		player.Velocity = launch_vector;
	}
}

/// Determines the launch vector based on the current power and angle of the launcher.
/// \return	The launch angle.
/// \author	CJ Harper
/// \date	04/28/2019
sf::Vector2<float> Launcher::DetermineLaunchVector()
{
	// The sin and cos functions only work with radians so we must convert the angle to radians first.
	constexpr float PI = 3.14159265;
	constexpr float CONVERT_DEGREES_TO_RADIANS = (PI / 180);
	const float radians = (AngleInDegrees * CONVERT_DEGREES_TO_RADIANS);

	// The y component is negative because negative implies moving upwards when drawing things to the screen.
	float y_component_of_vector = -(sin(radians) * Power);
	float x_component_of_vector = (cos(radians) * Power);

	sf::Vector2<float> launch_vector(x_component_of_vector, y_component_of_vector);
	return launch_vector;
}

void Launcher::draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const
{
    render_target.draw(PowerMeter);
	render_target.draw(AngleMeter);
}