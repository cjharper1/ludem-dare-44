#include "WorldMap.h"

/// Constructor.
/// \param[in]	player - The player character.
/// \param[in]	stage_hazards - The stage hazards on the world map.
/// \author	CJ Harper
/// \date	04/28/2019
WorldMap::WorldMap(const Player& player, const std::vector<StageHazard>& stage_hazards, const Launcher& launcher):
PlayerCharacter(player),
StageHazards(stage_hazards),
PlayerLauncher(launcher)
{}

/// Handles user input. Only keyboard events are supported at this time.
/// \param[in]	pressed_key - The key that the user pressed.
/// \author	CJ Harper
/// \date	04/28/2019
void WorldMap::HandleUserInput(const sf::Event& user_input)
{
	const bool move_launcher_to_next_state = (user_input.type == sf::Event::KeyPressed);
	if (move_launcher_to_next_state)
	{
		PlayerLauncher.MoveToNextState(PlayerCharacter);
	}
}

/// Update all items on the map.
/// \author	CJ Harper
/// \date	04/28/2019
void WorldMap::Update()
{
	// UPDATE THE PLAYER.
	PlayerCharacter.Update();

	// UPDATE THE LAUNCHER.
	PlayerLauncher.Update();

	// HANDLE ANY COLLISIONS THAT HAVE OCCURRED.
	HandleCollisions();
}

/// Handles any collisions that are currently occurring.
/// \author	CJ Harper
/// \date	04/28/2019
void WorldMap::HandleCollisions()
{
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
	// DRAW THE CHARACTER, STAGE HAZARDS, AND LAUNCHER.
	render_target.draw(PlayerCharacter);
	for (const StageHazard& stage_hazard : StageHazards)
	{
		render_target.draw(stage_hazard);
	}
	render_target.draw(PlayerLauncher);
}