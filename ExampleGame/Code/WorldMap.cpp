#include "WorldMap.h"

/// Constructor.
/// \param[in]	player - The player character.
/// \param[in]	stage_hazards - The stage hazards on the world map.
/// \author	CJ Harper
/// \date	04/28/2019
WorldMap::WorldMap(const Player& player, const std::vector<StageHazard>& stage_hazards):
PlayerCharacter(player),
StageHazards(stage_hazards)
{}

/// Handles user input. Only keyboard events are supported at this time.
/// \param[in]	pressed_key - The key that the user pressed.
/// \author	CJ Harper
/// \date	04/28/2019
void WorldMap::HandleUserInput(const sf::Event& user_input)
{
	// \todo Right now this is just moving the character around the screen, but
	//		this should be updated to handle launching the character once the launching
	//		mechanic is implemented.

	// HANDLE VERTICAL MOVEMENT.
	if (sf::Keyboard::isKeyPressed(sf::Keyboard::W))
	{
		PlayerCharacter.Velocity.y = -2;
	}
	else if (sf::Keyboard::isKeyPressed(sf::Keyboard::S))
	{
		PlayerCharacter.Velocity.y = 2;
	}
	else
	{
		PlayerCharacter.Velocity.y = 0;
	}

	// HANDLE HORIZONTAL MOVEMENT.
	if (sf::Keyboard::isKeyPressed(sf::Keyboard::A))
	{
		PlayerCharacter.Velocity.x = -2;
	}
	else if (sf::Keyboard::isKeyPressed(sf::Keyboard::D))
	{
		PlayerCharacter.Velocity.x = 2;
	}
	else
	{
		PlayerCharacter.Velocity.x = 0;
	}
}

/// Handles any collisions that are currently occurring.
/// \author	CJ Harper
/// \date	04/28/2019
void WorldMap::HandleCollisions()
{
	// UPDATE THE PLAYER.
	PlayerCharacter.Update();

	// CHECK IF THE PLAYER HAS COLLIDED WITH ANY STAGE HAZARDS.
	const BoundingBox player_hit_box = PlayerCharacter.GetHitBox();
	for (const StageHazard& stage_hazard : StageHazards)
	{
		const BoundingBox hazard_hit_box = stage_hazard.GetHitBox();
		const bool collision = hazard_hit_box.CheckCollision(player_hit_box);
		if (collision)
		{
			stage_hazard.UpdatePlayerMovement(PlayerCharacter);
		}
	}
}


void WorldMap::draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const
{
	// DRAW THE CHARACTER AND STAGE HAZARDS.
	render_target.draw(PlayerCharacter);
	for (const StageHazard& stage_hazard : StageHazards)
	{
		render_target.draw(stage_hazard);
	}
}