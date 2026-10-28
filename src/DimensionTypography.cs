public static class DimensionTypography
{
    public const float DefaultScale = 1.10f;
    public static (float Nominal,float Tolerance) Sizes(float scale)
    {
        if(!float.IsFinite(scale)||scale<=0||scale>3)throw new ArgumentOutOfRangeException(nameof(scale));
        return (12.5f*scale,8.5f*scale);
    }
}
