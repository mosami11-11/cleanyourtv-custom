package com.gathin.tvhome;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.drawable.GradientDrawable;
import android.media.MediaMetadata;
import android.media.session.MediaController;
import android.media.session.MediaSessionManager;
import android.media.session.PlaybackState;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.List;
public class NowPlayingCard {
    private LinearLayout card;
    private ImageView art;
    private TextView title, artist, btnPlay;
    private MediaController activeCtrl;
    private final Activity act;
    private final float d;
    public NowPlayingCard(Activity a, FrameLayout root) {
        this.act = a; this.d = a.getResources().getDisplayMetrics().density;
        build(root);
    }
    private TextView makeBtn(String txt, Runnable r) {
        TextView b = new TextView(act); b.setText(txt); b.setTextSize(15f);
        b.setTextColor(0xCCFFFFFF); b.setGravity(Gravity.CENTER);
        b.setFocusable(true); b.setClickable(true);
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(18 * d); bg.setColor(0x1AFFFFFF); b.setBackground(bg);
        b.setOnFocusChangeListener((v, f) -> {
            bg.setColor(f ? 0xFFFFFFFF : 0x1AFFFFFF);
            b.setTextColor(f ? 0xFF000000 : 0xCCFFFFFF);
            v.animate().scaleX(f ? 1.12f : 1f).scaleY(f ? 1.12f : 1f).setDuration(140).start();
        });
        b.setOnClickListener(v -> r.run());
        return b;
    }
    private void build(FrameLayout root) {
        card = new LinearLayout(act); card.setOrientation(LinearLayout.HORIZONTAL);
        card.setGravity(Gravity.CENTER_VERTICAL);
        int p = (int)(7 * d); card.setPadding(p, p, (int)(14 * d), p);
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(16 * d); bg.setColor(0x5518181C);
        bg.setStroke((int)(1 * d), 0x33FFFFFF); card.setBackground(bg);
        art = new ImageView(act); art.setScaleType(ImageView.ScaleType.CENTER_CROP);
        art.setClipToOutline(true);
        GradientDrawable abg = new GradientDrawable(); abg.setCornerRadius(10 * d);
        art.setBackground(abg);
        card.addView(art, new LinearLayout.LayoutParams((int)(42 * d), (int)(42 * d)));
        LinearLayout meta = new LinearLayout(act); meta.setOrientation(LinearLayout.VERTICAL);
        meta.setPadding((int)(12 * d), 0, (int)(12 * d), 0);
        title = new TextView(act); title.setTextColor(0xFFFFFFFF); title.setTextSize(14f);
        title.setSingleLine(true); title.setEllipsize(TextUtils.TruncateAt.END);
        artist = new TextView(act); artist.setTextColor(0xAAFFFFFF); artist.setTextSize(11.5f);
        artist.setSingleLine(true); artist.setEllipsize(TextUtils.TruncateAt.END);
        meta.addView(title); meta.addView(artist);
        card.addView(meta, new LinearLayout.LayoutParams((int)(155 * d), -2));
        int bs = (int)(34 * d); int bm = (int)(4 * d);
        TextView bPrev = makeBtn("|<", () -> { if (activeCtrl != null) activeCtrl.getTransportControls().skipToPrevious(); });
        btnPlay = makeBtn("||", () -> {
            if (activeCtrl == null) return;
            PlaybackState ps = activeCtrl.getPlaybackState();
            if (ps != null && ps.getState() == PlaybackState.STATE_PLAYING) activeCtrl.getTransportControls().pause();
            else activeCtrl.getTransportControls().play();
            card.postDelayed(this::refresh, 300);
        });
        TextView bNext = makeBtn(">|", () -> { if (activeCtrl != null) activeCtrl.getTransportControls().skipToNext(); });
        LinearLayout.LayoutParams lp1 = new LinearLayout.LayoutParams(bs, bs); lp1.setMargins(bm, 0, bm, 0);
        LinearLayout.LayoutParams lp2 = new LinearLayout.LayoutParams(bs, bs); lp2.setMargins(bm, 0, bm, 0);
        LinearLayout.LayoutParams lp3 = new LinearLayout.LayoutParams(bs, bs); lp3.setMargins(bm, 0, 0, 0);
        card.addView(bPrev, lp1); card.addView(btnPlay, lp2); card.addView(bNext, lp3);
        FrameLayout.LayoutParams clp = new FrameLayout.LayoutParams(-2, -2, Gravity.TOP | Gravity.LEFT);
        clp.leftMargin = (int)(58 * d); clp.topMargin = (int)(110 * d);
        card.setVisibility(View.GONE); root.addView(card, clp);
    }
    public void refresh() {
        try {
            MediaSessionManager msm = (MediaSessionManager) act.getSystemService(Context.MEDIA_SESSION_SERVICE);
            List<MediaController> cs = msm.getActiveSessions(new ComponentName(act, MediaNoteService.class));
            if (cs != null) for (MediaController c : cs) {
                MediaMetadata md = c.getMetadata(); PlaybackState ps = c.getPlaybackState();
                if (md == null) continue;
                CharSequence t = md.getText(MediaMetadata.METADATA_KEY_TITLE);
                if (TextUtils.isEmpty(t)) continue;
                activeCtrl = c; title.setText(t);
                CharSequence ar = md.getText(MediaMetadata.METADATA_KEY_ARTIST);
                artist.setText(!TextUtils.isEmpty(ar) ? ar : "Now Playing");
                Bitmap bmp = md.getBitmap(MediaMetadata.METADATA_KEY_ALBUM_ART);
                if (bmp == null) bmp = md.getBitmap(MediaMetadata.METADATA_KEY_ART);
                if (bmp != null) art.setImageBitmap(bmp); else art.setImageResource(R.drawable.ic_wifi);
                boolean pl = ps != null && ps.getState() == PlaybackState.STATE_PLAYING;
                btnPlay.setText(pl ? "||" : ">");
                card.setVisibility(View.VISIBLE); return;
            }
        } catch (Exception ignored) {}
        card.setVisibility(View.GONE);
    }
}
