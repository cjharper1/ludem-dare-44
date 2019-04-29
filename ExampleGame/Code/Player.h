#pragma once

#include "SFML/System/Vector2.hpp"
#include "SFML/Graphics.hpp"
#include "BoundingBox.h"

class Player : public sf::Drawable
{
    public:
        Player(const sf::Vector2<float>& initial_position, const sf::VideoMode& screen_resolution);
        
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
		const unsigned int HEIGHT_IN_PIXELS = 24;
		const unsigned int WIDTH_IN_PIXELS = 24;

    private:
		virtual void draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const;

        // The hit box for the player.
		BoundingBox HitBox;

		// The sprite sheet for the player
		sf::Texture Texture;

		// Box within the sheet for the sprite
		sf::IntRect TextureRect;

        // The image representing the player.
        sf::Sprite Sprite;

		// Information tracked for animation purposes
		enum Animation {hit = 0, launch = 1, boost = 2, idle = 3};
		Animation CurrentAnimation;
		Animation PreviousAnimation;
		// number of game 'ticks' the current animation has been held
		int frameCount;
		const int TICKS_PER_FRAME = 4;

		unsigned int ScreenWidth;
		unsigned int ScreenHeight;
};