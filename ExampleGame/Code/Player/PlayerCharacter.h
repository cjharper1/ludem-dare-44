/// Represents the character the player controls.
/// \author CJ Harper
/// \date   03/07/2018
public class PlayerCharacter
{
    public:
    PlayerCharacter();
    
    /// Gets the X position of the player characer.
    float GetXPosition() {return XPosition;}
    
    /// Gets the Y position of the player character.
    float GetYPosition() {return YPosition;}
    
    private:
    float XPosition;
    float YPosition;
}