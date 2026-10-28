public readonly record struct Point2(float X,float Y);

// Geometric families supply envelopes; the policy knows no holes, plates or field letters.
public record ScaleEnvelope(float WidthMm,float HeightMm,float AvailableWidthMm,float AvailableHeightMm);
public record ScalePolicy(float ReferenceSpanMm=286,float PreferredDenominator=2.5f,float CompactRatio=.7f);
public static class LayoutPolicy
{
    public static float ChooseScale(ScaleEnvelope envelope,ScalePolicy policy)
    {
        if(envelope.WidthMm<=0||envelope.HeightMm<=0||envelope.AvailableWidthMm<=0||envelope.AvailableHeightMm<=0||policy.ReferenceSpanMm<=0||policy.PreferredDenominator<=0)
            throw new ArgumentException("Geçersiz yerleşim boyutları.");
        bool compact=Math.Max(envelope.WidthMm,envelope.HeightMm)<policy.ReferenceSpanMm*policy.CompactRatio;
        float preferred=compact?Math.Max(1,policy.PreferredDenominator*.8f):policy.PreferredDenominator;
        var fits=new[]{1f,2f,2.5f,5f,10f,20f,50f,100f}.Where(n=>envelope.WidthMm/n<=envelope.AvailableWidthMm&&envelope.HeightMm/n<=envelope.AvailableHeightMm).ToArray();
        if(fits.Length==0)throw new Exception("Geometri ayrılan alana sığmıyor.");
        return fits.OrderBy(n=>Math.Abs(Math.Log(n/preferred))).First();
    }
    public static (float Angle,Point2 TextAnchor) LeaderLabel(Point2 tip,Point2 end,float clearance)
    {
        float dx=end.X-tip.X,dy=end.Y-tip.Y;
        if(dx*dx+dy*dy<1)throw new ArgumentException("Lider çizgisi sıfır uzunlukta.");
        float angle=MathF.Atan2(dy,dx);if(angle>MathF.PI/2)angle-=MathF.PI;if(angle< -MathF.PI/2)angle+=MathF.PI;
        return (angle*180/MathF.PI,new Point2(end.X+MathF.Sin(angle)*clearance,end.Y-MathF.Cos(angle)*clearance));
    }
}
