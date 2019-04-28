#pragma once

#include "SFML/Graphics.hpp"
#include "BoundingBox.h"
#include "Player.h"

/// Represents the various types of hazards that can be encountered.
enum HazardType
{
    Cactus,
    Scissors,
    Spike
};

/// Represents any potential stage hazard the player could run into.
class StageHazard : public sf::Drawable
{
    public:
        StageHazard(const HazardType type, const sf::Vector2<float>& position);
    
		void UpdatePlayerMovement(Player& player) const;

		/// \return	The hit box for this hazard.
		BoundingBox GetHitBox() const { return HitBox; }
        
    private:
		virtual void draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const;

		/// The hit box for this hazard.
		BoundingBox HitBox;

        /// The type of stage hazard this is.
        HazardType Type;
        
        /// The image used to represent this hazard.
		/// \todo Replace this with the sf::Sprite class when we have actual art.
        sf::RectangleShape Sprite;
};