#pragma once

#include "SFML/System/Vector2.hpp"
#include "SFML/Graphics.hpp"
#include "BoundingBox.h"

class Player : public sf::Drawable
{
    public:
        Player();
        
        void Update();
        
        // The current velocity of the player.
        sf::Vector2<float> Velocity;
        
        // The current angle of rotation of the player in degrees
        // starting with straight up as 0 degrees. So facing right
        // would be 90 degrees, facing down would be 180, facing left
        // would be 270, etc.
        float AngleOfRotationInDegrees;

		/// \return The player's hit box.
		BoundingBox GetHitBox() const { return HitBox; }

    private:
		virtual void draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const;

        // The hit box for the player.
		BoundingBox HitBox;

        // The image representing the player.
		// \todo Replace this with sf::Sprite class when we have art.
        sf::RectangleShape Sprite;
};