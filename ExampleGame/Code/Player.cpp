#include "Player.h"

/// Constructor.
/// \author CJ Harper
/// \date   04/28/2019
Player::Player():
Velocity(sf::Vector2<float>(0,0)),
AngleOfRotationInDegrees(0),
HitBox(sf::Vector2<float>(0,0), sf::Vector2<float>(24,24)),
Sprite()
{

	Texture.loadFromFile("Assets/player.png");
	TextureRect = sf::IntRect(0, HEIGHT_IN_PIXELS * idle, WIDTH_IN_PIXELS, HEIGHT_IN_PIXELS);
	Sprite.setTexture(Texture);
	Sprite.setTextureRect(TextureRect);

	CurrentAnimation = idle;
	PreviousAnimation = idle;
	frameCount = 0;
}

/// Updates properties of the player such as position, velocity, and rotation. 
/// This should be called each game tick.
/// \author CJ Harper
/// \date   04/28/2019
void Player::Update()
{
    // UPDATE THE PLAYER HITBOX BASED ON CURRENT VELOCITY.
	HitBox.Translate(Velocity);

	// MOVE THE PLAYER BACK IN BOUNDS IF THEY HAVE MOVED OUT OF BOUNDS.
	constexpr float MINIMUM_IN_BOUNDS_VALUE = 0;
	const float current_player_x_coordinate = HitBox.GetTopLeftCoordinate().x;
	const float current_player_y_coordinate = HitBox.GetTopLeftCoordinate().y;
	const bool x_position_out_of_bounds = (current_player_x_coordinate < MINIMUM_IN_BOUNDS_VALUE);
	if (x_position_out_of_bounds)
	{
		// Reset the player x coordinate.
		HitBox.SetPosition(sf::Vector2<float>(MINIMUM_IN_BOUNDS_VALUE, current_player_y_coordinate));
	}
	const bool y_position_out_of_bounds = (current_player_y_coordinate < MINIMUM_IN_BOUNDS_VALUE);
	if (y_position_out_of_bounds)
	{
		// Reset the player y coordinate.
		HitBox.SetPosition(sf::Vector2<float>(current_player_x_coordinate, MINIMUM_IN_BOUNDS_VALUE));
	}

	// ALIGN THE PLAYER SPRITE WITH THEIR HITBOX.
	Sprite.setPosition(HitBox.GetTopLeftCoordinate());
    
    // APPLY THE CURRENT ROTATION TO THE PLAYER SPRITE.
    Sprite.rotate(AngleOfRotationInDegrees);

	// Animation logic
	if (CurrentAnimation != PreviousAnimation)
	{
		frameCount = 0;
		TextureRect.left = 0;
		TextureRect.top = CurrentAnimation * HEIGHT_IN_PIXELS;
		PreviousAnimation = CurrentAnimation;
	}
	else
	{
		frameCount++;
		if (frameCount == TICKS_PER_FRAME)
		{
			TextureRect.left = (TextureRect.left + WIDTH_IN_PIXELS) % (WIDTH_IN_PIXELS * 4);
			frameCount = 0;
		}
	}

	Sprite.setTextureRect(TextureRect);

	// \todo Apply gravity or some sort of velocity decay?
}

void Player::draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const
{
	// DRAW THE CHARACTER TO THE SCREEN.

	render_target.draw(Sprite);
}