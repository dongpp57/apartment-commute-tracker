# Setup Guide

Hướng dẫn cài đặt apartment-commute-tracker từ A→Z. Anh làm 1 lần, sau đó cron tự chạy.

## 1. Tạo Google Cloud project + API key

1. Truy cập https://console.cloud.google.com
2. Click "Select a project" (góc trên) → "New Project" → đặt tên `commute-tracker` → Create
3. Vào sidebar "APIs & Services" → "Library" → search **Distance Matrix API** → click "Enable"
4. Vào "APIs & Services" → "Credentials" → "Create credentials" → "API key" → copy key (lưu lại)
5. (Khuyến nghị) Click "Restrict key" → chọn "API restrictions" → "Restrict key" → tick chỉ "Distance Matrix API" → Save

## 2. Set quota limit (tránh charge bất ngờ)

1. Vào "APIs & Services" → "Distance Matrix API" → tab "Quotas & System Limits"
2. Set "Elements per day" ≤ 1000 (task này chỉ dùng ~20 elements/ngày, dư thoải mái)
3. Vào "Billing" → "Budgets & alerts" → "Create budget":
   - Amount: $5/tháng
   - Alert threshold: 50%, 90%, 100%
   - Email khi vượt ngưỡng
4. Confirm

## 3. Tạo GitHub repo + push code

```bash
cd /Users/lap60812_local/Documents/AI/Move
git remote add origin git@github.com:<your-username>/apartment-commute-tracker.git
git push -u origin main
```

Nếu chưa có SSH key, dùng HTTPS:
```bash
git remote add origin https://github.com/<your-username>/apartment-commute-tracker.git
git push -u origin main
```

Repo phải **public** để dùng GitHub Pages free (data không nhạy cảm — list BĐS công khai + thời gian commute).

## 4. Add API key vào GitHub Secrets

GitHub repo → Settings → Secrets and variables → Actions → "New repository secret"
- Name: `GOOGLE_MAPS_API_KEY`
- Secret: paste API key từ bước 1
- Add secret

## 5. Bật GitHub Pages

GitHub repo → Settings → Pages → "Build and deployment" source: chọn **GitHub Actions**

(Không dùng "Deploy from a branch" — workflow của project này deploy qua Actions)

## 6. Trigger workflow lần đầu

GitHub repo → Actions → chọn workflow "Track Commute" → "Run workflow" → chọn slot `0700` → Run.

Đợi ~1-2 phút:
- Job `track` chạy: gọi API, log dữ liệu, commit
- Job `deploy-pages` chạy: deploy report lên Pages

Khi xong, vào Settings → Pages sẽ thấy URL dạng `https://<your-username>.github.io/apartment-commute-tracker/`

## 7. Sau đó cron tự chạy

- 7:00 ICT mỗi ngày: cron tự gọi API, log, deploy report
- 7:30 ICT mỗi ngày: tương tự
- Anh xem report bất kỳ lúc nào qua URL Pages

## Sửa danh sách chung cư

Anh muốn thêm/bớt cụm:

```bash
# Sửa file local
vim data/apartments.json

# Hoặc sửa trên GitHub web (mở file → Edit pencil icon)

git add data/apartments.json
git commit -m "data: update apartment list"
git push
```

Lần cron tiếp theo sẽ dùng list mới.

## Xem log thô + thống kê local

```bash
git pull
source .venv/bin/activate
python scripts/report.py --cli-only
```

In ra terminal bảng thống kê các cụm.

## Recalibrate motorbike factor

Sau ~2 tuần data, Anh có thể tự đi xe máy 1 lần lúc 7:00 từ 1 cụm cụ thể về Vincom NCT để đo thực tế. Nếu thấy chênh nhiều với `duration_motorcycle_min` trong log, sửa `MOTO_FACTOR` trong `scripts/lib/config.py`:

- Default: `0.88` (xe máy nhanh hơn ô tô ~12%)
- Nếu Anh đi nhanh hơn dự đoán: giảm factor về `0.80-0.85`
- Nếu chậm hơn: tăng về `0.92-0.95`

Commit + push, lần cron tiếp theo dùng factor mới.

## Troubleshooting

| Vấn đề | Hướng xử lý |
|---|---|
| Workflow fail bước "Track commute" với `OVER_QUERY_LIMIT` | Vào Google Cloud Console → tăng quota Distance Matrix API |
| Workflow fail với `403 Forbidden` | API key bị restrict sai. Kiểm tra restriction "API restrictions" có tick Distance Matrix API |
| Workflow fail bước "Commit" | Repo chưa cấp `contents: write` permission. Settings → Actions → General → Workflow permissions → "Read and write" |
| GitHub Pages 404 | Settings → Pages source phải là "GitHub Actions" (không phải "Deploy from a branch") |
| Cron không chạy đúng giờ | GitHub Actions cron có thể delay 5-15 phút khi load cao. Acceptable cho mục đích thống kê trung bình |
