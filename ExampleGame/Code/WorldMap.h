#pragma once

#include "SFML/Graphics/Drawable.hpp"
#include "Launcher.h"
#include "Player.h"
#include "StageHazard.h"

/// Represents the overworld and includes all objects in it such as the player, walls, stage hazards, etc.
/// This can be used to track the position of objects and determine if there are collisions.
/// \author CJ Harper
/// \date   04/28/2019
class WorldMap : public sf::Drawable
{
    public:
		WorldMap(const Player& player, const std::vector<StageHazard>& stage_hazards, const Launcher& launcher);
        
		void HandleUserInput(const sf::Event& user_input);
		void Update();
    
    private:
		void HandleCollisions();
		virtual void draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const;

		Player PlayerCharacter;
		std::vector<StageHazard> StageHazards;
		Launcher PlayerLauncher;
};