# Research Log — Considered Apartment Clusters

Tất cả các cụm chung cư em đã research khi shortlist 10 cụm cho pipeline. File này tránh việc research lại từ đầu nếu sau này Anh muốn xem xét lại.

**Tiêu chí filter ban đầu (2026-05-04):**
- Budget: 2PN ≤ 5.2 tỉ VND (giá trần ~5 tỉ)
- Loại căn hộ: 2 phòng ngủ (vợ chồng son)
- Vị trí: bất kỳ hướng nào quanh Hà Nội, ≤ 30 phút đi xe máy giờ cao điểm tới Vincom Nguyễn Chí Thanh
- Tiêu chí: cân bằng (i) thời gian đi làm, (ii) tiềm năng tăng giá, (iii) chất lượng sống

---

## ✅ 10 cụm trong shortlist

Xem chi tiết tại [`apartments.json`](./apartments.json) và [dashboard live](https://dongpp57.github.io/apartment-commute-tracker/).

| Cụm | District | Giá 2PN | Commute (motorbike peak) |
|---|---|---|---|
| HD Mon City | Nam Từ Liêm | 4.8-5.0 tỉ | 14p |
| Mỹ Đình Pearl | Nam Từ Liêm | 3.4-4.0 tỉ | 12p |
| Vinhomes Smart City | Nam Từ Liêm | 4.8 tỉ | 18p |
| Iris Garden | Nam Từ Liêm | 4.0-4.7 tỉ | 18p |
| **Hoàng Thành Pearl** ✨ | Nam Từ Liêm | 5.0-5.6 tỉ | ~18p (chưa calibrate) |
| Hateco Apollo | Nam Từ Liêm | 3.9-4.5 tỉ | 22p |
| Sunshine Riverside | Tây Hồ | 5.0 tỉ | 15p |
| Mipec Riverside | Long Biên | 4.5 tỉ | 21p |
| Hồ Gươm Plaza | Hà Đông | 4.3-5.0 tỉ | 17p |
| Eco Green City | Thanh Trì | 4.9-5.0 tỉ | 13p |

---

## ❌ Các cụm đã loại — Lý do

### Loại sau khi đã track (swap với cụm khác)

| Cụm | District | Giá 2PN | Lý do |
|---|---|---|---|
| **Vinhomes Ocean Park 1** | Gia Lâm | 4.9-5.05 tỉ (63-75m²) | Calibrated motorbike commute = 39p, vượt threshold 30p Anh đặt ra. Distance 20.9 km — cụm xa nhất trong list. Swap với Hoàng Thành Pearl (2026-05-05) vì gần ga tàu + commute ngắn hơn. Vẫn là cụm tốt về dài hạn (Vinhomes ecosystem, Metro tương lai) — Anh có thể re-add nếu nâng threshold lên 40p. |

### Loại vì vượt budget 5 tỉ

| Cụm | District | Giá 2PN | Lý do chi tiết |
|---|---|---|---|
| **The Matrix One** | Nam Từ Liêm (Mễ Trì) | 7.95-9.99 tỉ (87-89m²) | Cao cấp MIK Group, vị trí tốt nhưng giá quá tầm. Diện tích 2PN start từ 86m² nên tổng giá cao dù giá/m² hợp lý. |
| **Mandarin Garden** | Cầu Giấy (Trung Hòa) | ~11-13 tỉ (114m²) | Giá ~100 triệu/m². 2PN diện tích lớn 114m² → tổng cao. |
| **Imperia Sky Garden** | Hai Bà Trưng (Minh Khai) | 7.9-9 tỉ (76-82m²) | ~100 triệu/m². Vị trí gần trung tâm nhưng vượt budget rõ rệt. |
| **Mipec Rubik 360** | Cầu Giấy (Xuân Thủy) | 8-10.8 tỉ (70-85m²) | Cao cấp Mipec, đường Xuân Thủy đắc địa. Quá tầm. |
| **Vinhomes Times City Park Hill** | Hai Bà Trưng | 7-8.8 tỉ (64-75m²) | Premium Vingroup, vị trí cận trung tâm. |
| **D'Capitale Trần Duy Hưng** | Cầu Giấy | 8.8-10.5 tỉ (68-73m²) | Vinhomes brand premium, Trần Duy Hưng là đường vàng. |
| **Royal City** | Thanh Xuân | (không research kỹ) | Em assume vượt budget vì là Vinhomes premium đã định giá cao. Có thể research lại nếu Anh quan tâm. |
| **Goldmark City** | Bắc Từ Liêm (Hồ Tùng Mậu) | 6.3-7.5 tỉ (68-86m²) | Borderline trên budget, loại để có space cho cụm khác. |
| **Anland Premium** | Hà Đông (Tố Hữu) | 6-6.7 tỉ (70-75m²) | Nam Cường, vị trí Tố Hữu OK nhưng giá vượt 1 tỉ. |
| **The Terra An Hưng** | Hà Đông (Dương Nội) | 6.2-6.75 tỉ (74m²) | Văn Phú-Invest, 60-70 triệu/m². Vượt budget. |
| **Thăng Long Number One** | Nam Từ Liêm (Mễ Trì) | 7.5+ tỉ (92-95m²) | Anh hỏi nhắc cụ thể. Em đã add tạm rồi remove vì 2PN min 92m² nên tổng quá tầm. Vị trí siêu tốt (Đại lộ Thăng Long), commute ~11p — nếu Anh sau này nâng budget lên 7-8 tỉ thì cụm này đáng cân nhắc. |

### Loại vì rủi ro / chưa bàn giao

| Cụm | District | Giá 2PN | Lý do |
|---|---|---|---|
| **FLC Twin Towers (265 Cầu Giấy)** | Cầu Giấy | 4.5+ tỉ (97m²) | Đang xây foundation, dự kiến bàn giao cuối 2026/đầu 2027. Risk: FLC Group có vấn đề tài chính, dự án có thể chậm. Tránh tiền cọc bị "đóng băng". |

### Loại vì giá thấp hơn budget rõ rệt (chất lượng dưới mức Anh muốn)

| Cụm | District | Giá 2PN | Lý do |
|---|---|---|---|
| **HH Linh Đàm** | Hoàng Mai | 1.5-2.5 tỉ | Giá quá rẻ, mật độ cực cao, an ninh kém, không đáng cân nhắc cho vợ chồng son. |
| **FLC Garden City Đại Mỗ** | Nam Từ Liêm | 3.75-4.5 tỉ (56-66m²) | Trong budget nhưng diện tích nhỏ + chất lượng FLC rủi ro. Em ưu tiên Hateco Apollo / Iris Garden cùng khu. |
| **Discovery Complex 302 Cầu Giấy** | Cầu Giấy | 3.1-3.2 tỉ | Giá rẻ bất thường, có thể chỉ là sale ưu đãi giai đoạn đầu hoặc căn diện tích nhỏ/tầng thấp. Cần verify thêm nếu Anh quan tâm. |

### Có thể research thêm trong tương lai

Các khu sau em chưa research kỹ vì đã đủ 10 cụm với diversity tốt. Nếu Anh muốn add thêm hoặc swap, có thể bắt đầu từ đây:

- **Mỹ Đình Plaza 2** (Nam Từ Liêm)
- **Golden Park Tower** (Cầu Giấy)
- **N04 Hoàng Đạo Thúy** (Cầu Giấy)
- **Le Grand Jardin Sài Đồng** (Long Biên) — 5.45-7.9 tỉ, borderline
- **D'. El Dorado Tây Hồ** (Tây Hồ)
- **Mipec Rubik 360** (đã loại trên, có thể research căn nhỏ nhất)
- **Times City** (Hai Bà Trưng) — phân khu T1-T11 cũ, giá có thể mềm hơn Park Hill
- **Royal City** (Thanh Xuân) — phân khu R1-R6, cần check giá thực

---

## Notes

**Diversity của shortlist 10 cụm:**
- 6 districts (Nam Từ Liêm 5 cụm, Hà Đông 1, Tây Hồ 1, Long Biên 1, Thanh Trì 1, Gia Lâm 1)
- 5 cao_cap + 5 trung_cap
- Giá range 3.4-5.05 tỉ
- Commute range 12-39 phút

**Ưu tiên Nam Từ Liêm:** 5/10 cụm — vì khu này có nhiều dự án trong budget + gần Vincom NCT về mặt route. Anh nói lúc đầu *"khu Cầu Giấy/Mỹ Đình có nhiều dự án"* nên em ưu tiên cluster ở đây.

**Khu vực thiếu trong shortlist:**
- Cầu Giấy (đã consider nhiều, đa số vượt budget)
- Hai Bà Trưng (Times City, Imperia, D'Capitale đều vượt)
- Đông Anh, Sóc Sơn (xa, không research)

---

**Last updated:** 2026-05-05
**Maintained by:** Pipeline tracker — update khi Anh add/remove cụm.
