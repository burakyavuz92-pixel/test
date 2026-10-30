using System.Text.Json.Nodes;
using System.Text.Json;

public static class FeatureSectionTrace
{
    static double[] V(JsonNode? n)=>n!.AsArray().Select(x=>x!.GetValue<double>()).ToArray();
    static double[] Add(double[] a,double[] b)=>a.Zip(b).Select(t=>t.First+t.Second).ToArray();
    static double[] Sub(double[] a,double[] b)=>a.Zip(b).Select(t=>t.First-t.Second).ToArray();
    static double[] Mul(double[] a,double k)=>a.Select(x=>x*k).ToArray();
    static double Dot(double[] a,double[] b)=>a.Zip(b).Sum(t=>t.First*t.Second);
    static double[] Cross(double[] a,double[] b)=>new[]{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};
    static double[] Unit(double[] a){double d=Math.Sqrt(Dot(a,a));if(d<1e-9)throw new Exception("Kesit referans yönü geçersiz.");return Mul(a,1/d);}
    // Check finite segments in the source-view projection, not infinite supporting planes.
    public static bool CoversProjectedPoint(IReadOnlyList<double[]> path,double[] point,double tolerance=1e-7)
    {
        for(int i=1;i<path.Count;i++)
        {
            var a=path[i-1];var b=path[i];double dx=b[0]-a[0],dy=b[1]-a[1],length2=dx*dx+dy*dy;
            if(length2<1e-20)continue;
            double t=Math.Clamp(((point[0]-a[0])*dx+(point[1]-a[1])*dy)/length2,0,1);
            double ex=point[0]-(a[0]+t*dx),ey=point[1]-(a[1]+t*dy);
            if(ex*ex+ey*ey<=tolerance*tolerance)return true;
        }
        return false;
    }
    public static JsonArray Expand(JsonArray sections,JsonNode resolved)
    {
        var ops=resolved["operations"]!.AsArray().ToDictionary(o=>o!["id"]!.GetValue<string>());
        var frames=resolved["frames"]!.AsArray().ToDictionary(o=>o!["id"]!.GetValue<string>());
        var views=resolved["views"]!.AsArray().ToDictionary(o=>o!["id"]!.GetValue<string>());
        double[] World(string frame,double[] p){var f=frames[frame]!;var x=V(f["xAxis"]);var z=V(f["zAxis"]);return Add(V(f["origin"]),Add(Add(Mul(x,p[0]),Mul(Cross(z,x),p[1])),Mul(z,p[2])));}
        double[]? Anchor(JsonNode reference)
        {
            string id=reference["feature"]!.GetValue<string>();
            if(resolved["featureApplied"]?[id] is null)throw new Exception("Kesit özelliği bilinmiyor: "+id);
            if(!resolved["featureApplied"]![id]!.GetValue<bool>())return null;
            var op=ops[id]!;string frame=op["frame"]!.GetValue<string>();var args=op["args"]!;
            string entity=reference["entity"]!.GetValue<string>();if(entity=="frameOrigin")return World(frame,new double[3]);
            if(entity!="axis")throw new Exception("Kesit referansı desteklenmiyor.");
            string kind=op["op"]!.GetValue<string>();double[] point;
            if(kind is "hole" or "cylinder")point=V(args["origin"]);
            else if(kind=="revolve")point=V(args["axisOrigin"]);
            else if(kind is "extrude" or "throughExtrude")
            {
                var sketch=ops[op["inputs"]![0]!.GetValue<string>()]!;var loops=sketch["args"]!["loops"]!.AsArray();
                if((loops.Count!=1&&sketch["args"]!["profileHoles"]?.GetValue<bool>()!=true)||loops[0]!["kind"]!.GetValue<string>()!="circle")throw new Exception("Bu profil için eksen referansı yok; frameOrigin kullanılabilir.");
                var xy=V(loops[0]!["center"]);string plane=sketch["args"]!["plane"]!.GetValue<string>();
                point=plane switch{"XY"=>new[]{xy[0],xy[1],0.0},"XZ"=>new[]{xy[0],0.0,xy[1]},"YZ"=>new[]{0.0,xy[0],xy[1]},_=>throw new Exception("Profil düzlemi bilinmiyor.")};frame=sketch["frame"]!.GetValue<string>();
            }
            else if(kind=="circularPattern")
            {
                int index=reference["instance"]?.GetValue<int>()??throw new Exception("Desen kesit referansı instance ister.");
                int count=(int)args["count"]!.GetValue<double>();if(index<0||index>=count)throw new Exception("Kesit desen örneği aralık dışında.");
                var axis=Unit(V(args["axis"]));var x=Sub(new[]{1.0,0,0},Mul(axis,axis[0]));if(Dot(x,x)<1e-9)x=Sub(new[]{0.0,1,0},Mul(axis,axis[1]));x=Unit(x);var y=Cross(axis,x);
                double angle=(args["startAngleDeg"]!.GetValue<double>()+index*args["totalAngleDeg"]!.GetValue<double>()/count)*Math.PI/180;
                double radius=args["pitchDiameter"]!.GetValue<double>()/2;point=Add(V(args["center"]),Add(Mul(x,radius*Math.Cos(angle)),Mul(y,radius*Math.Sin(angle))));
            }
            else throw new Exception("Özellik ekseni henüz desteklenmiyor: "+kind);
            return World(frame,point);
        }
        var result=new JsonArray();
        foreach(var source in sections)
        {
            if(source!["kind"]!.GetValue<string>()!="featureTrace"){result.Add(source.DeepClone());continue;}
            var main=Anchor(source["main"]!)??throw new Exception("Kesit ana referansı mevcut değil.");
            var view=views[source["view"]!.GetValue<string>()]!;var parent=views[source["sourceView"]!.GetValue<string>()]!;
            var sweep=Unit(V(parent["direction"]));var normal=Unit(V(view["direction"]));if(Math.Abs(Dot(sweep,normal))>1e-3)throw new Exception("Kesit ve kaynak görünüş yönleri dik olmalı.");
            var along=Unit(Cross(normal,sweep));if(Dot(along,V(parent["up"]))<0)along=Mul(along,-1);
            var points=source["through"]!.AsArray().Select(a=>Anchor(a!)).Where(a=>a is not null).Select(a=>new[]{Dot(Sub(a!,main),normal),Dot(Sub(a!,main),along)}).Prepend(new double[2]).OrderByDescending(a=>a[1]).ToList();
            // Stable sorting preserves reference order for equal longitudinal positions.
            // Conservative presentation extent; native executor can later clip to actual BRep bounds.
            double extent=10;
            foreach(var p in resolved["parameters"]!.AsObject())if(p.Value is JsonValue value&&value.TryGetValue<double>(out var n)&&double.IsFinite(n))extent=Math.Max(extent,Math.Abs(n)*2+10);
            foreach(var p in points)extent=Math.Max(extent,Math.Abs(p[1])+10);
            var trace=new List<double[]>{new[]{0.0,extent}};double u=0,prev=extent;
            foreach(var p in points){if(Math.Abs(p[0]-u)>1e-7){double jog=(prev+p[1])/2;trace.Add(new[]{u,jog});trace.Add(new[]{p[0],jog});}trace.Add(p);u=p[0];prev=p[1];}
            if(Math.Abs(u)>1e-7){double jog=(prev-extent)/2;trace.Add(new[]{u,jog});trace.Add(new[]{0.0,jog});}trace.Add(new[]{0.0,-extent});
            var clean=new List<double[]>();foreach(var p in trace)if(clean.Count==0||Math.Abs(p[0]-clean[^1][0])+Math.Abs(p[1]-clean[^1][1])>1e-7)clean.Add(p);
            if(points.Any(p=>!CoversProjectedPoint(clean,p)))
                throw new Exception("Kesit yolu mevcut referansların tümünden geçmiyor.");
            bool planar=clean.All(p=>Math.Abs(p[0])<1e-7);var output=source.DeepClone();output["kind"]=planar?"planar":"stepped";
            var world=clean.Select(p=>Add(main,Add(Mul(normal,p[0]),Mul(along,p[1])))).ToArray();
            if(planar){output["frame"]="__sectionWorld";output["plane"]=new JsonObject{["point"]=JsonSerializer.SerializeToNode(main),["normal"]=JsonSerializer.SerializeToNode(normal)};}
            else{output.AsObject().Remove("sourceView");output["frame"]="__sectionWorld";output["path"]=JsonSerializer.SerializeToNode(world);output["extrusionDirection"]=JsonSerializer.SerializeToNode(sweep);}
            result.Add(output);
        }
        return result;
    }
}
