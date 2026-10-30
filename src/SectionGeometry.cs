using System.Text.Json.Nodes;

// Derives cutting surfaces locally. No part-family or hole-count assumptions.
public static class SectionGeometry
{
    static double[] Vec(JsonNode? n,int size=3)
    {
        var v=n!.AsArray().Select(x=>x!.GetValue<double>()).ToArray();
        if(v.Length!=size||v.Any(x=>!double.IsFinite(x)))throw new Exception("Geçersiz kesit koordinatı/yönü.");
        return v;
    }
    static double[] Add(double[] a,double[] b)=>a.Zip(b).Select(t=>t.First+t.Second).ToArray();
    static double[] Sub(double[] a,double[] b)=>a.Zip(b).Select(t=>t.First-t.Second).ToArray();
    static double[] Scale(double[] a,double k)=>a.Select(x=>x*k).ToArray();
    static double Dot(double[] a,double[] b)=>a.Zip(b).Sum(t=>t.First*t.Second);
    static double[] Cross(double[] a,double[] b)=>new[]{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};
    static double[] Unit(double[] a)
    {
        double len=Math.Sqrt(Dot(a,a));if(len<1e-10)throw new Exception("Kesit yönü sıfır olamaz.");return Scale(a,1/len);
    }
    public static JsonArray Resolve(JsonArray sections,JsonArray frames,JsonArray views)
    {
        var f=frames.ToDictionary(x=>x!["id"]!.GetValue<string>());var v=views.ToDictionary(x=>x!["id"]!.GetValue<string>());var result=new JsonArray();
        foreach(var source in sections)
        {
            var s=source!.DeepClone();string kind=s["kind"]!.GetValue<string>();
            string viewId=s["view"]!.GetValue<string>();if(!v.TryGetValue(viewId,out var view))throw new Exception("Kesit görünüşü bilinmiyor.");
            var camera=Unit(Vec(view!["direction"]));
            double[] Transform(double[] xyz,bool point)
            {
                var frame=f[s["frame"]!.GetValue<string>()]!;
                var x=Vec(frame["xAxis"]);var z=Vec(frame["zAxis"]);var y=Cross(z,x);
                var rotated=Add(Add(Scale(x,xyz[0]),Scale(y,xyz[1])),Scale(z,xyz[2]));
                return point?Add(Vec(frame["origin"]),rotated):rotated;
            }
            var planes=new JsonArray();
            if(kind=="planar")
            {
                double[] point,normal;
                if(s["plane"] is JsonObject plane)
                {
                    point=Transform(Vec(plane["point"]),true);normal=Unit(Transform(Vec(plane["normal"]),false));
                }
                else // Historical v7 trace records: derive faithfully, never silently repair.
                {
                    var path=s["path"]!.AsArray();if(path.Count!=2)throw new Exception("Düz kesit iki nokta ister.");
                    point=Transform(Vec(path[0]),true);
                    normal=Unit(Cross(Transform(Sub(Vec(path[1]),Vec(path[0])),false),Transform(Vec(s["extrusionDirection"]),false)));
                }
                if(Math.Abs(Dot(normal,camera))<.999)throw new Exception("Kesit düzlemi normali kesit görünüş yönüyle uyumlu değil.");
                planes.Add(new JsonObject{["point"]=JsonSerializerNode(point),["normal"]=JsonSerializerNode(normal)});
            }
            else if(kind=="stepped")
            {
                var path=s["path"]!.AsArray();var world=new List<double[]>();double[] sweep;
                if(s["sourceView"] is JsonValue sourceView)
                {
                    if(!v.TryGetValue(sourceView.GetValue<string>(),out var parent))throw new Exception("Kesit izinin kaynak görünüşü bilinmiyor.");
                    sweep=Unit(Vec(parent!["direction"]));var up=Vec(parent["up"]);up=Unit(Sub(up,Scale(sweep,Dot(up,sweep))));var right=Unit(Cross(up,sweep));
                    var origin=Vec(s["origin"]);
                    foreach(var p in path){var xy=Vec(p,2);world.Add(Add(origin,Add(Scale(right,xy[0]),Scale(up,xy[1]))));}
                }
                else
                {
                    sweep=Unit(Transform(Vec(s["extrusionDirection"]),false));foreach(var p in path)world.Add(Transform(Vec(p),true));
                }
                if(world.Count<3)throw new Exception("Kademeli kesit en az üç nokta ister.");
                bool aligned=false;
                for(int i=1;i<world.Count;i++)
                {
                    var normal=Unit(Cross(Sub(world[i],world[i-1]),sweep));
                    aligned|=Math.Abs(Dot(normal,camera))>.999;
                    planes.Add(new JsonObject{["point"]=JsonSerializerNode(world[i-1]),["normal"]=JsonSerializerNode(normal)});
                }
                if(!aligned)throw new Exception("Kesit yolu kesit görünüş yönüyle uyumlu değil.");
                s["worldPath"]=JsonSerializerNode(world);s["sweepDirection"]=JsonSerializerNode(sweep);
            }
            else throw new Exception("Kesit türü desteklenmiyor.");
            s["cuttingPlanes"]=planes;result.Add(s);
        }
        return result;
    }
    static JsonNode JsonSerializerNode<T>(T value)=>System.Text.Json.JsonSerializer.SerializeToNode(value)!;
}
