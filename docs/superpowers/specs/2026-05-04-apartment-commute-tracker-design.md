# Apartment Commute Tracker — Design Spec

**Date:** 2026-05-04
**Owner:** Anh Đông (dongpp57@gmail.com)
**Status:** Draft, awaiting user review

---

## 1. Mục tiêu

Hỗ trợ Anh Đông (đang ở Thường Tín, làm việc tại Vincom Nguyễn Chí Thanh, Hà Nội) chọn căn hộ chung cư để mua với:

- Budget: giá trần ~5 tỉ VND (tìm các căn 4.8 – 5.2 tỉ)
- Diện tích: 2 phòng ngủ (vợ chồng son, dự phòng cho con sau này / WFH)
- Phạm vi: bất kỳ hướng nào quanh Hà Nội, miễn ≤ 30 phút đi xe máy giờ cao điểm tới Vincom Nguyễn Chí Thanh
- Tiêu chí: cân bằng (i) thời gian đi làm, (ii) tiềm năng tăng giá, (iii) chất lượng sống

Output gồm 2 phần:

1. **Shortlist 10 cụm chung cư** tiềm năng (file `apartments.json`).
2. **Pipeline đo thời gian đi xe máy** từ 10 cụm này tới Vincom Nguyễn Chí Thanh, mỗi ngày 7h00 và 7h30, tích lũy log để thống kê trung bình.

## 2. Non-goals

- Không build web dashboard real-time (script CLI + static HTML là đủ).
- Không track giá BĐS theo thời gian (chỉ track commute time).
- Không gửi notification (Anh chủ động vào repo / GitHub Pages xem).
- Không tự động ra quyết định mua — chỉ cung cấp data, Anh ra quyết định.

## 3. Kiến trúc tổng thể (2 phase)

### Phase 1 — Research (one-shot)

Em research và xuất `data/apartments.json` gồm 10 cụm chung cư đại diện. Anh review, thêm/bớt/sửa, rồi approve.

### Phase 2 — Tracking pipeline (recurring)

GitHub Actions cron chạy lúc 7h00 và 7h30 ICT mỗi ngày, gọi Google Maps Distance Matrix API đo thời gian từ 10 cụm tới Vincom Nguyễn Chí Thanh, append vào `data/commute_log.csv`, regenerate `reports/latest.html`, auto-commit về repo. Anh xem dashboard qua GitHub Pages.

## 4. Phase 1: Research Output

### 4.1 Quy trình research

1. Web search các trang BĐS Việt Nam: batdongsan.com.vn, nhatot.com, cafeland.vn, alonhadat.com.vn, meeyland.com.
2. Filter theo: 2PN, giá 4.5 – 5.2 tỉ, vị trí ≤ ~12km hoặc ≤ ~30 phút driving giờ cao điểm tới Vincom Nguyễn Chí Thanh.
3. Lấy tọa độ chính xác từ Google Maps cho mỗi cụm.
4. Đảm bảo diversity: trải đều cao cấp / trung cấp / mới bàn giao, và trải các hướng (Cầu Giấy, Nam Từ Liêm, Thanh Xuân, Hà Đông, Hoàng Mai, Tây Hồ, Long Biên).
5. Pre-filter các khu cần check kỹ (theo input của Anh, đặc biệt **khu Cầu Giấy có nhiều dự án** — bao gồm HD Mon City, Mandarin Garden, Discovery Complex, FLC Green Apartment, Golden Park Tower, N04 Hoàng Đạo Thúy, v.v.).

### 4.2 Schema `data/apartments.json`

```json
[
  {
    "id": "vinhomes-smart-city",
    "cluster_name": "Vinhomes Smart City",
    "district": "Nam Từ Liêm",
    "representative_address": "Tây Mỗ, Nam Từ Liêm, Hà Nội",
    "lat": 21.0145,
    "lng": 105.7423,
    "category": "cao_cap",
    "sample_units": [
      {
        "tower": "Sapphire 1",
        "area_m2": 68,
        "bedrooms": 2,
        "price_billion_vnd": 4.8,
        "status": "đã bàn giao",
        "source_url": "https://..."
      }
    ],
    "pros": ["Tiện ích nội khu đầy đủ", "Cộng đồng trẻ", "Tuyến Metro số 5 tương lai"],
    "cons": ["Xa trung tâm", "Mật độ cao"],
    "estimated_commute_min": 28,
    "investment_potential": "Cao - hạ tầng phía Tây phát triển mạnh",
    "data_collected_date": "2026-05-04"
  }
]
```

### 4.3 User review checkpoint

Sau khi xuất `apartments.json`, Anh có quyền:
- Thêm cụm em miss
- Bỏ cụm Anh không thích
- Sửa thông tin nếu sai

→ Sau khi Anh approve `apartments.json` → mới sang Phase 2.

### 4.4 Caveats

- Giá BĐS biến động hàng tuần. `data_collected_date` ghi rõ trong file. Sau 2-3 tháng cần refresh nếu Anh vẫn đang dùng pipeline.
- Em research bằng web search → có thể có dự án mới em chưa biết, hoặc giá em ghi không khớp 100% với realtor. Anh là người ra quyết định cuối, em chỉ shortlist.

## 5. Phase 2: Pipeline Architecture

### 5.1 Cấu trúc thư mục repo

```
apartment-commute-tracker/
├── .github/
│   └── workflows/
│       └── track-commute.yml      # Cron 7h00 + 7h30 ICT hằng ngày
├── data/
│   ├── apartments.json            # 10 cụm (output Phase 1)
│   └── commute_log.csv            # Log tích lũy (auto-append)
├── scripts/
│   ├── track_commute.py           # Gọi Google Maps API, ghi log
│   └── report.py                  # Sinh báo cáo thống kê
├── reports/
│   └── latest.html                # Dashboard HTML (auto-generate)
├── requirements.txt
└── README.md
```

### 5.2 Data flow per cron run

1. GitHub Actions trigger (cron)
2. Checkout repo
3. Install Python deps
4. Run `track_commute.py`:
   - Loop qua 10 cụm trong `apartments.json`
   - Với mỗi cụm, gọi Google Maps Distance Matrix API:
     - `origin`: lat/lng của cụm
     - `destination`: Vincom Nguyễn Chí Thanh (`21.0245, 105.8095` — sẽ verify lại tọa độ chính xác khi implement)
     - `mode`: `driving`
     - `departure_time`: `now`
     - `traffic_model`: `best_guess`
   - Append row vào `data/commute_log.csv`
5. Run `report.py` → regenerate `reports/latest.html`
6. `git add` + `git commit` + `git push` log + report về repo
7. GitHub Pages tự deploy `reports/latest.html`

### 5.3 Schema `data/commute_log.csv`

| Column | Type | Description |
|---|---|---|
| `timestamp_ict` | ISO 8601 (+07:00) | Thời điểm đo |
| `apartment_id` | string | Khớp với `id` trong apartments.json |
| `slot` | enum `0700` / `0730` | Slot cron nào |
| `duration_min` | float | Thời gian không tính traffic (driving) |
| `duration_in_traffic_min` | float | Thời gian có traffic (best_guess) |
| `duration_motorcycle_min` | float | `duration_in_traffic_min × MOTO_FACTOR` |
| `distance_km` | float | Khoảng cách |
| `status` | enum `OK` / `ERROR_<reason>` | Trạng thái call |

Ví dụ:

```
timestamp_ict,apartment_id,slot,duration_min,duration_in_traffic_min,duration_motorcycle_min,distance_km,status
2026-05-05T07:00:00+07:00,vinhomes-smart-city,0700,18.5,22.1,19.4,9.4,OK
2026-05-05T07:00:00+07:00,royal-city,0700,,,,,ERROR_quota_exceeded
```

### 5.4 Cron schedule

GitHub Actions chạy theo UTC. Vietnam = UTC+7.

```yaml
on:
  schedule:
    - cron: '0 0 * * *'    # 7h00 ICT (= 00:00 UTC)
    - cron: '30 0 * * *'   # 7h30 ICT (= 00:30 UTC)
  workflow_dispatch:        # Cho phép trigger manual
```

**Caveat:** GitHub Actions cron có thể delay 5-15 phút khi cluster load cao. Acceptable vì mục đích là thống kê trung bình, không cần precise đến phút.

### 5.5 Error handling

- API call fail (quota, network, invalid response) → ghi row với `status=ERROR_<reason>`, **không** break loop (vẫn đo các cụm còn lại).
- Workflow fail toàn bộ → GitHub gửi email cho Anh.
- API key sai / thiếu → fail-fast ngay request đầu, log rõ lỗi.

### 5.6 Configuration

| Item | Where | Notes |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | GitHub Secrets | Encrypted, không lộ ra log |
| Destination coords | Hardcode trong `track_commute.py` | Vincom Nguyễn Chí Thanh, sẽ verify khi implement |
| `MOTO_FACTOR` | Constant trong script (default `0.88`) | Configurable. Sau 2 tuần Anh có thể tự đi xe máy 1 lần để calibrate |
| Apartment list | `data/apartments.json` | Anh có thể edit trực tiếp file này, push lên repo |

## 6. Reporting & Statistics

### 6.1 Layer 1 — `report.py` (CLI)

Chạy `python scripts/report.py` local sau `git pull`. Output ra terminal:

- Bảng thống kê cho từng slot (7:00 và 7:30) gồm: mean, p50 (median), p90, min, max, std, samples
- Bảng so sánh slot 7:00 vs 7:30 cho từng cụm (Δ phút)
- Ranking các cụm theo `mean` của slot 7:00 với marker `⭐ Recommended` cho top 3
- Cờ cảnh báo:
  - `⚠️` nếu p90 > 30 phút (vượt ngưỡng Anh đặt ra)
  - `🎲` nếu std > 8 phút (không ổn định)

### 6.2 Layer 2 — `reports/latest.html`

Static HTML standalone (không cần server), auto-generate sau mỗi lần cron chạy. Gồm:

- Bảng tổng hợp giống Layer 1, sortable
- Line chart thời gian theo ngày cho từng cụm (Chart.js CDN)
- Bar chart ranking by mean commute
- Heatmap ngày trong tuần × slot (xem thứ mấy / giờ nào kẹt nhất)
- Last updated timestamp

### 6.3 GitHub Pages

- Repo **public** (data không nhạy cảm — chỉ là list công khai trên các trang BĐS + thời gian commute).
- Bật GitHub Pages free, source = `main` branch, folder = `/reports`.
- URL: `https://<github-username>.github.io/apartment-commute-tracker/latest.html`
- Anh xem từ điện thoại bất kỳ lúc nào.

### 6.4 Computed metrics

Cho mỗi `(apartment_id, slot)`:

- `mean` — trung bình
- `p50` — median (quan trọng hơn mean vì loại outlier)
- `p90` — "ngày tệ nhất hợp lý" (90% ngày Anh đến nhanh hơn con số này)
- `min` / `max` — best / worst case
- `std` — độ ổn định
- `samples` — số ngày có data (độ tin cậy)

Sau **30 ngày data**, em sẽ đề xuất Anh review lại list (loại bớt cụm tệ, focus 3-5 cụm top).

## 7. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| HTTP client | `requests` |
| Data | `pandas` |
| HTML render | `jinja2` |
| Chart | `Chart.js` (CDN, no build step) |
| Cron | GitHub Actions (`ubuntu-latest`) |
| API | Google Maps Distance Matrix API |
| Storage | Git (CSV in repo) |
| Hosting | GitHub Pages |

**Cost estimate:**
- GitHub Actions: ~30 giây × 60 lần/tháng = 30 phút/tháng → free (free tier 2000 phút).
- Google Maps API: 10 cụm × 2 slot × 30 ngày = 600 request/tháng × $5/1000 = $3/tháng → free (free credit $200/tháng).

## 8. Implementation Order

1. **Phase 1** — Research & shortlist 10 cụm → `data/apartments.json`
2. **User checkpoint** — Anh review apartments.json
3. **Phase 2.1** — Code `track_commute.py`, test local 1 lần để verify API hoạt động
4. **Phase 2.2** — Code `report.py` + HTML template
5. **Phase 2.3** — Code GitHub Actions workflow `track-commute.yml`
6. **Phase 2.4** — Setup hướng dẫn step-by-step cho Anh:
   - Tạo GitHub repo public
   - Tạo Google Cloud project + enable Distance Matrix API + tạo API key + set quota limit
   - Add API key vào GitHub Secrets
   - Bật GitHub Pages
   - Trigger 1 lần manual để verify
7. **Phase 2.5** — Monitor 2-3 ngày đầu để chắc chắn cron chạy đúng

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Google Maps không có mode "motorcycle" cho VN | Dùng `driving × MOTO_FACTOR` (default 0.88), configurable. Anh có thể tự đi 1 lần sau 2 tuần để calibrate factor |
| GitHub Actions cron delay 5-15 phút | Acceptable — mục đích thống kê trung bình |
| Giá BĐS biến động | `data_collected_date` ghi rõ. Refresh sau 2-3 tháng nếu cần |
| API key bị leak | Lưu trong GitHub Secrets (encrypted). Set quota limit trong Google Cloud Console (max ~$5/tháng) để tránh charge bất ngờ |
| Repo public lộ thông tin cá nhân | Code không chứa secret. `apartments.json` chỉ là data BĐS công khai. Log commute chỉ là số phút di chuyển — không lộ địa chỉ nhà Anh (vì Anh chưa ở đó) |
| Cron miss 1 ngày (GitHub outage) | Acceptable — sample size 30+ ngày sẽ smooth out outlier |

## 10. Acceptance Criteria

Project hoàn thành khi:

- [ ] `data/apartments.json` có 10 cụm chung cư, mỗi cụm có đủ field theo schema 4.2, và Anh đã approve list này
- [ ] `track_commute.py` chạy thành công, append đúng row vào `commute_log.csv`
- [ ] `report.py` in ra bảng thống kê đúng format Section 6.1
- [ ] `reports/latest.html` render được trên trình duyệt với chart hiển thị đúng
- [ ] GitHub Actions workflow chạy thành công 2 lần/ngày trong **3 ngày liên tiếp** (verify cron stable)
- [ ] GitHub Pages hoạt động, Anh xem được report qua URL từ điện thoại
- [ ] Sau 7 ngày, Anh có ít nhất 14 data point cho mỗi cụm × slot

## 11. Open Questions / Future Work

- Sau 30 ngày data, có thể cân nhắc thêm slot 18h00 / 18h30 (giờ cao điểm chiều về) để đo round-trip.
- Nếu Anh muốn so sánh public transport (metro / bus) vs xe máy, có thể thêm mode `transit` trong API call (cùng pipeline, thêm column).
- Có thể tích hợp thêm dữ liệu giá BĐS theo tháng (scrape batdongsan.com.vn) nếu Anh muốn theo dõi giá trong khi đợi tracking đủ 30 ngày.
