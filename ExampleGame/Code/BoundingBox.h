#pragma once

#include "SFML/System/Vector2.hpp"

/// A square area representing the boundaries of an object.
/// \author CJ Harper
/// \date   04/28/2019
class BoundingBox
{
    public:
        BoundingBox(const sf::Vector2<float>& top_left_position, const sf::Vector2<float>& dimensions);
		void Translate(const sf::Vector2<float>& translation);
		void SetPosition(const sf::Vector2<float>& new_top_left_position);
        bool CheckCollision(const BoundingBox& other) const;

		sf::Vector2<float> GetTopLeftCoordinate() const { return TopLeftCoordinate; }
        
    private:
        bool CheckIfContainsCoordinate(const sf::Vector2<float>& coordinate) const;
        sf::Vector2<float> TopLeftCoordinate;
        sf::Vector2<float> BottomLeftCoordinate;
        sf::Vector2<float> TopRightCoordinate;
        sf::Vector2<float> BottomRightCoordinate;
};