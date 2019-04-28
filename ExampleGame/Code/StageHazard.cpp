#include "SFML/Graphics/RectangleShape.hpp"
#include "SFML/System.hpp"
#include "StageHazard.h"

/// Constructor.
/// \todo The hitbox is arbitrarily being set to 10 by 10 right now as a placeholder. This will need to be updated when we
///		figure out how large each hazard will be.
/// \param[in]  type - The type of hazard this is.
/// \param[in]	position - The position of this hazard.
/// \author CJ Harper
/// \date   04/28/2019
StageHazard::StageHazard(const HazardType type, const sf::Vector2<float>& position):
HitBox(position, sf::Vector2<float>(10, 10)),
Type(type),
Sprite()
{
    // SET THE ART THAT WILL BE USED TO REPRESENT THE HAZARD.
    // \todo Replace placeholder art with real art.
    constexpr unsigned int HEIGHT_IN_PIXELS = 10;
    constexpr unsigned int WIDTH_IN_PIXELS = 10;
    sf::Vector2<float> placeholder_size(HEIGHT_IN_PIXELS, WIDTH_IN_PIXELS);
    sf::RectangleShape placeholder_art(placeholder_size);
	placeholder_art.setPosition(position);
    Sprite = placeholder_art;
    switch (Type)
    {
        case (HazardType::Cactus):
        {
            Sprite = placeholder_art;
            break;
        }
        case (HazardType::Scissors):
        {
            Sprite = placeholder_art;
            break;
        }
        case (HazardType::Spike):
        {
            Sprite = placeholder_art;
            break;
        }
		default:
        {
            // This case should not happen in practice, but
            // if it does, placeholder art will be used.
            Sprite = placeholder_art;
        }
    }
}

/// Updates the current way the player is moving. This should typically only be called
/// if the player has run into the hazard.
/// \param[in,out]  player - The player to update the movement for.
/// \author CJ Harper
/// \date   04/28/2019
void StageHazard::UpdatePlayerMovement(Player& player) const
{
    // UPDATE THE PLAYER VELOCITY AND ANGLE BASED ON HAZARD TYPE.
    // \todo Figure out values for these.
    switch (Type)
    {
        case (HazardType::Cactus):
        {
			player.Velocity = sf::Vector2<float>(0, 0);
            player.AngleOfRotationInDegrees = 0;

            break;
        }
        case (HazardType::Scissors):
        {
			player.Velocity = sf::Vector2<float>(0, 0);
            player.AngleOfRotationInDegrees = 0;
            break;
        }
        case (HazardType::Spike):
        {
			player.Velocity = sf::Vector2<float>(0, 0);
            player.AngleOfRotationInDegrees = 0;
            break;
        }
        default:
        {
            // This is unexpected so no changes will be made to the player
            // to avoid unintended gameplay behavior.
            return;
        }
    }
}

void StageHazard::draw(sf::RenderTarget& render_target, sf::RenderStates render_states) const
{
	render_target.draw(Sprite);
}