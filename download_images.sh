#!/bin/zsh
# ============================================================
# some-draw.page 画像一括ダウンロード & HTMLパス書き換え
# Mac (zsh) 対応版
# ============================================================

set -e
IMAGES_DIR="images"
mkdir -p "$IMAGES_DIR"

echo "📥 画像をダウンロード中..."
echo ""

IMAGES=(
"hero_sakura.jpg|https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/623957e2-22bf-4656-8bd6-b27690aa0539/20231101_sakura_chikayori2_srbg/w=1920,quality=90,fit=scale-down"
"news_kanazawacraft.jpg|https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/421f33b2-1675-469f-8be4-d7e2780dd956/kanazawacraft_ogp_img/w=640,quality=80,fit=scale-down"
"ex_houmaku.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/5588b747-03b2-41ae-b4b2-4649005e4acf/series_of_houmaku_1.jpg"
"ex_flowers_journey.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/86a79e3f-50a3-4ece-8b07-95f48cf01966/DMura.jpg"
"ex_artfair2023.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/bc84bfd9-554b-4bc8-801d-ac993fe4e0cd/DSC06581-%E5%BC%B7%E5%8C%96_1%E3%81%AE%E3%82%B3%E3%83%94%E3%83%BC.jpg"
"ex_souvin.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/a66cb852-abe2-45a4-b17b-d37f6ae0284c/_DSC5714.jpg"
"ex_doctor2022.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6bfc8346-09ed-4467-85b9-ceae9ffe0274/20231102line_full.jpg"
"ex_100colors.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/20939df3-832b-4217-91a9-c4b0ace4865f/20231112_2021sketch02_full.jpg"
"ex_doctor2021.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/3f36949f-19ec-4813-8537-55272479e948/20231112_2021sketch02_exhibition.jpg"
"ex_artbase.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6e9edd00-6955-451a-bb1f-7eb3d3ae7b90/20231113artbasekoten.jpg"
"ex_artnagoya.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/a9c6062a-f31d-4340-84e2-0ee7d90e0e38/20231114artnagoya2.jpg"
"ex_assenble.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/e847a699-5066-4168-b1bc-e9e2b845242e/PC203199.jpg"
"ex_butokan.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6f75a4e0-80b8-459c-86b4-cd28fd32d748/2019-10-04_13-10-56_543.jpg"
"ex_portreport.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/4e534409-0f03-401d-b8b4-6a97941d6060/20231113kasabuta_exhibition.jpg"
"ex_artsplanet.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/4c7a5d9f-dc9e-4c2f-b6f9-ea95452304e1/DSC_1254.jpg"
"ex_toiya.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/b2a6f2d7-3252-446e-aa5a-5eb10c8e9ee7/toiya.jpg"
"ex_visualsonic.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/c4652b17-9f64-4994-b04c-15bdcb04e865/mitasu02.jpg"
"ex_real.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/7ad4b5fa-58d7-4c4a-9755-0c6684d7d60e/f.jpg"
"w_houmaku_series.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/b95069aa-c493-4318-8ad9-e16bd6342b4f/series_of_houmaku_1.jpg"
"w_sketch_tulip02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/4527467c-bb27-40fb-84b8-7ee3dff38d5f/insta_tulip2.jpg"
"w_sketch_yukitsubaki.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/c8862807-2e7c-404f-9a32-10989826a46b/frame_%E3%82%B9%E3%82%AF%E3%82%A8%E3%82%A2.jpg"
"w_magnolia.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/5915295a-d11d-462b-a45b-724af2aba529/EA12D744-49CE-443B-849A-2F6E8A532A65.jpeg"
"w_omokage_sky.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/00b19874-8e63-4604-b776-95e442485137/20240601_30stand_sky3-.jpg"
"w_astrantia.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/0ca25b2a-2fcd-4488-88fd-bb501f651377/20240601_20stand_astrantia3.jpg"
"w_calla_lily.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/93fbf437-fabb-4421-86b1-5414ca3c4af9/_DSC8572.jpg"
"w_sketch_tulip01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/542001db-53f6-48be-b3a2-332e836d80ef/frame2_2.jpg"
"w_tulip02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/8d05f542-ac4b-4bc8-a98c-bbf4d29a7ae9/_DSC8533_2.jpg"
"w_omokage_water.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/b0d4a223-683c-47a4-ab8f-de0cc39dad08/20240601_30standwater2.jpg"
"w_omokage_tulip01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/157a1b34-add8-4801-89a0-e46147ad3562/%E9%9D%A2%E5%BD%B1tulip01_2.jpg"
"w_sketch_sarusuberi.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/ffd2ee58-daa1-4710-88bf-be5481bcc132/IMG_9704cut.jpg"
"w_poppy.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/f5ee26dc-d948-40f0-ac82-d17e28a57401/_DSC8694.jpg"
"w_tulip.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6f84eccb-9384-4145-ae9d-d84637fd2415/IWAI_DMback_20240225.jpg"
"w_sakura.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/e0168024-548e-4efd-9a1f-9d84f9ebf340/20231102sakurafull.jpg"
"w_mitsu.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6fcf463d-634e-4135-870d-aa51d3321df7/mitsu_full.jpg"
"w_flowercells_coral.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/093c3ad9-27f4-4907-bd36-36002f3b68e8/flower-cells-coral-and-blue-colors-.jpg"
"w_flowercells_red.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/9975000a-c661-4729-8107-783e6fa0de00/works_of_redhydrangea.jpg"
"w_flowercells_blue.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/593287cc-f99f-4c85-a1e6-b2ab2b568a0e/20231102bluehypofull.jpg"
"w_flowercells_camellia.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/0c864a6e-0418-412b-99f3-a4672af6d695/camelia_full.jpg"
"w_kokuoku11.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/1032fb79-e40f-4451-8e37-dc6acdd088d9/20231104kokuoku11.jpg"
"w_kokuoku06.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/e631c631-8d5f-4947-9c06-ac16b9b462b6/20231104kokuoku06.jpg"
"w_kokuoku05.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/e38f4201-b955-42d7-9125-2ab0544e552c/20231104kokuoku05.jpg"
"w_mizuasobi.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/ce9f0705-c418-4de7-8c50-4ef85da9822e/20231104mizuasobi.jpg"
"w_poppy2.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/a3b365a3-b82a-47e6-98de-1b94195abaf3/20231104poppy.jpg"
"w_ajisai.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/48c81c38-6f60-4c73-902e-e2a609d36765/20231105ajisai_full.jpg"
"w_kokuoku04.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/353f998f-dbee-4057-957a-5a98caac5b20/20231105syakuyaku_front.jpg"
"w_kokuoku03.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/c19224be-d593-4091-9e0b-51b27d8961a4/20231105kokuoku3.jpg"
"w_halipuu.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/75bae949-b48c-45ca-a947-04c04da8976b/20231105halipuu02.jpg"
"w_kokuoku02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/7b018156-f67b-4b8d-9b8a-7e25dd91f7ba/20231112kokuoku02_full.jpg"
"w_kokuoku01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/6883d8cc-c76d-48a0-9423-6445698ea1ec/20231108kokuoku01_center.jpg"
"w_line03.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/cdb7cc4d-4e4f-4abc-a876-e11d0f74335b/20231112line02_full.jpg"
"w_line02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/00c9bb64-dc76-4254-87ed-96e149b09e9e/20231112line02tree_full2.jpg"
"w_sketch2021a.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/2415b5da-be04-47c9-9f63-946b0fd7b653/20231112_2021sketch02_full.jpg"
"w_sketch2021b.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/593da403-9a55-4bc9-8245-4843dc0dbbfa/20231112_2021sketch02_full2.jpg"
"w_tree02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/31d42727-e982-4e90-9811-5cca1bcffa81/20231112tree2_full.jpg"
"w_tree01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/d96e623d-15ec-4cf3-bee6-bc38b3e6b813/2231112tree01_full.jpg"
"w_dyedweeping02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/0a923080-8906-4ea7-8a9b-f1439d27e383/20231113dyedweeping02_full.jpg"
"w_dyedweeping01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/15ca984b-08db-4a1b-a059-ce9177d66f7c/20231113dyedweeping01_full.jpg"
"w_boumaku08.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/43ca72a0-e75b-47c9-89b0-981c887c130d/20231113boumaku08full.jpg"
"w_observation.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/263aeb24-d8d6-452d-b2a8-39e866e8480d/20231113observation.jpg"
"w_uncontrol.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/415492a8-08aa-45da-8a66-4f46540d7cd6/20231113uncontrol.jpg"
"w_boumaku07.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/8b2625bc-8546-4a81-9ec3-ce76f3dc835b/20231113boumaku7_full.jpg"
"w_glue.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/51b62c4b-68b1-414f-9896-c8e27e351733/20231113glue_full.jpg"
"w_kasabuta03.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/41683a82-4356-49f1-b24a-41ba6b7e151d/20231113_kasabuta3_full.jpg"
"w_tokiwokiku.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/5b9171c4-ac9b-41fe-9bc8-af489b00316e/20231114tokiwokiku_full.jpg"
"w_apiece02.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/e86d9651-a536-40c5-80a2-2ec26257bf14/20231114apiece02_full.jpg"
"w_apiece01.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/21338a64-66f6-401b-881c-ecaa315757c9/20231115_piece01_full.jpg"
"w_irokara.jpg|https://assets.super.so/80b91c4b-80a0-4aa5-a025-de63b6059b6f/images/1a22715b-c479-4d49-84ee-65ca5663b81c/20231115irokara.jpg"
)

TOTAL=${#IMAGES[@]}
COUNT=0
FAILED=0

for entry in "${IMAGES[@]}"; do
    filename="${entry%%|*}"
    url="${entry#*|}"
    COUNT=$((COUNT + 1))

    if [ -f "$IMAGES_DIR/$filename" ]; then
        echo "  [$COUNT/$TOTAL] ⏭  $filename (skip)"
        continue
    fi

    echo "  [$COUNT/$TOTAL] ⬇  $filename"
    if curl -sL -o "$IMAGES_DIR/$filename" "$url"; then
        SIZE=$(wc -c < "$IMAGES_DIR/$filename" 2>/dev/null | tr -d ' ')
        if [ "$SIZE" -lt 1000 ]; then
            echo "           ⚠  小さいファイル ($SIZE bytes)"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "           ❌ 失敗"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "📥 ダウンロード完了: $((COUNT - FAILED))/$TOTAL"

echo ""
echo "🔄 HTMLの画像パスを書き換え中..."

for entry in "${IMAGES[@]}"; do
    filename="${entry%%|*}"
    url="${entry#*|}"

    [ -f index.html ] && sed -i '' "s|${url}|images/${filename}|g" index.html 2>/dev/null || true
    [ -f works.html ] && sed -i '' "s|${url}|images/${filename}|g" works.html 2>/dev/null || true

    for exfile in exhibitions/*.html; do
        [ -f "$exfile" ] && sed -i '' "s|${url}|../images/${filename}|g" "$exfile" 2>/dev/null || true
    done
done

sed -i '' "s|https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/623957e2-22bf-4656-8bd6-b27690aa0539/20231101_sakura_chikayori2_srbg/w=1920,quality=90,fit=scale-down|images/hero_sakura.jpg|g" index.html 2>/dev/null || true

echo ""
echo "✅ 完了！"
echo ""
echo "サイト構成:"
echo "  index.html"
echo "  works.html"
echo "  style.css"
echo "  exhibitions/ ($(ls -1 exhibitions/*.html 2>/dev/null | wc -l | tr -d ' ') pages)"
echo "  images/ ($(ls -1 $IMAGES_DIR 2>/dev/null | wc -l | tr -d ' ') files)"
echo ""
echo "👉 次: このフォルダごと GitHub にpushしてください"
